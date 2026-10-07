"""
Database repositories for data access layer.
"""
from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID

from sqlalchemy import desc, func, or_, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    NewsArticle,
    NewsCategory,
    RefreshLog,
    SentimentType,
    User,
    UserBookmark,
    UserPreferences,
    UserReadHistory,
)


class UserRepository:
    """User data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        email: str,
        username: str,
        password_hash: str,
    ) -> User:
        user = User(email=email.lower(), username=username.lower(), password_hash=password_hash)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(func.lower(User.email) == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(func.lower(User.username) == username.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(func.count()).select_from(User).where(func.lower(User.email) == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar() > 0

    async def exists_by_username(self, username: str) -> bool:
        stmt = select(func.count()).select_from(User).where(func.lower(User.username) == username.lower())
        result = await self.session.execute(stmt)
        return result.scalar() > 0

    async def update_last_login(self, user_id: UUID) -> None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            user.last_login_at = datetime.now(timezone.utc)

    async def update_username(self, user_id: UUID, new_username: str) -> User | None:
        user = await self.get_by_id(user_id)
        if user:
            user.username = new_username.lower()
            user.updated_at = datetime.now(timezone.utc)
            await self.session.flush()
        return user


class UserPreferencesRepository:
    """User preferences data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> UserPreferences | None:
        stmt = select(UserPreferences).where(UserPreferences.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        user_id: UUID,
        preferred_categories: list[str] | None = None,
        preferred_sources: list[str] | None = None,
        preferred_language: str | None = None,
    ) -> UserPreferences:
        prefs = await self.get_by_user_id(user_id)
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            self.session.add(prefs)

        if preferred_categories is not None:
            prefs.preferred_categories = preferred_categories
        if preferred_sources is not None:
            prefs.preferred_sources = preferred_sources
        if preferred_language is not None:
            prefs.preferred_language = preferred_language

        prefs.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return prefs


class NewsArticleRepository:
    """News article data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, article: NewsArticle) -> NewsArticle:
        self.session.add(article)
        await self.session.flush()
        return article

    async def bulk_create(self, articles: list[NewsArticle]) -> list[NewsArticle]:
        self.session.add_all(articles)
        await self.session.flush()
        return articles

    async def get_by_id(self, article_id: UUID) -> NewsArticle | None:
        return await self.session.get(NewsArticle, article_id)

    async def get_by_canonical_url(self, canonical_url: str) -> NewsArticle | None:
        stmt = select(NewsArticle).where(NewsArticle.canonical_url == canonical_url)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_id: str, source_name: str) -> NewsArticle | None:
        stmt = select(NewsArticle).where(
            NewsArticle.external_id == external_id,
            NewsArticle.source_name == source_name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_url(self, url: str) -> bool:
        stmt = select(func.count()).select_from(NewsArticle).where(NewsArticle.url == url)
        result = await self.session.execute(stmt)
        return result.scalar() > 0

    async def exists_by_canonical_url(self, canonical_url: str) -> bool:
        stmt = select(func.count()).select_from(NewsArticle).where(NewsArticle.canonical_url == canonical_url)
        result = await self.session.execute(stmt)
        return result.scalar() > 0

    async def get_latest(
        self,
        category: NewsCategory | None = None,
        limit: int = 20,
        offset: int = 0,
        exclude_duplicates: bool = True,
    ) -> Sequence[NewsArticle]:
        stmt = select(NewsArticle)
        if exclude_duplicates:
            stmt = stmt.where(NewsArticle.is_duplicate == False)
        if category:
            stmt = stmt.where(NewsArticle.category == category)
        stmt = stmt.order_by(desc(NewsArticle.published_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_importance(
        self,
        category: NewsCategory | None = None,
        limit: int = 20,
        offset: int = 0,
        min_importance: float = 0.0,
    ) -> Sequence[NewsArticle]:
        stmt = select(NewsArticle).where(
            NewsArticle.is_duplicate == False,
            NewsArticle.importance_score >= min_importance,
        )
        if category:
            stmt = stmt.where(NewsArticle.category == category)
        stmt = stmt.order_by(
            desc(NewsArticle.importance_score), desc(NewsArticle.published_at)
        ).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_trending(
        self,
        category: NewsCategory | None = None,
        limit: int = 20,
        offset: int = 0,
        hours: int = 24,
    ) -> Sequence[NewsArticle]:
        """Get trending articles based on engagement and freshness."""
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        stmt = select(NewsArticle).where(
            NewsArticle.is_duplicate == False,
            NewsArticle.published_at >= cutoff,
        )
        if category:
            stmt = stmt.where(NewsArticle.category == category)
        # Trending score: importance * recency factor
        stmt = stmt.order_by(
            desc(NewsArticle.importance_score * func.extract('epoch', NewsArticle.published_at)),
        ).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search(
        self,
        query: str,
        category: NewsCategory | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Sequence[NewsArticle]:
        """Full-text search on title, description, content."""
        search_vector = func.to_tsvector('english', NewsArticle.title + ' ' + 
            func.coalesce(NewsArticle.description, '') + ' ' + 
            func.coalesce(NewsArticle.content, ''))
        search_query = func.plainto_tsquery('english', query)
        
        stmt = select(NewsArticle).where(
            NewsArticle.is_duplicate == False,
            search_vector.op('@@')(search_query),
        )
        if category:
            stmt = stmt.where(NewsArticle.category == category)
        stmt = stmt.order_by(
            desc(func.ts_rank_cd(search_vector, search_query)),
            desc(NewsArticle.published_at),
        ).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_personalized_feed(
        self,
        user_id: UUID,
        preferred_categories: list[str],
        limit: int = 20,
        offset: int = 0,
    ) -> Sequence[NewsArticle]:
        """Get personalized feed based on user preferences."""
        from app.db.models import UserReadHistory
        
        # Subquery for read article IDs
        read_subq = select(UserReadHistory.article_id).where(
            UserReadHistory.user_id == user_id
        )
        
        stmt = select(NewsArticle).where(
            NewsArticle.is_duplicate == False,
            ~NewsArticle.id.in_(read_subq),  # Exclude already read
        )
        
        if preferred_categories:
            # Convert string categories to enum
            cat_enums = [NewsCategory(c) for c in preferred_categories if c in NewsCategory.__members__.values()]
            if cat_enums:
                stmt = stmt.where(NewsArticle.category.in_(cat_enums))
        
        # Order by: category match, importance, freshness
        stmt = stmt.order_by(
            desc(NewsArticle.category.in_(cat_enums) if preferred_categories else False),
            desc(NewsArticle.importance_score),
            desc(NewsArticle.published_at),
        ).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_latest(self, category: NewsCategory | None = None) -> int:
        stmt = select(func.count()).select_from(NewsArticle).where(NewsArticle.is_duplicate == False)
        if category:
            stmt = stmt.where(NewsArticle.category == category)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_search(self, query: str, category: NewsCategory | None = None) -> int:
        search_vector = func.to_tsvector('english', NewsArticle.title + ' ' + 
            func.coalesce(NewsArticle.description, '') + ' ' + 
            func.coalesce(NewsArticle.content, ''))
        search_query = func.plainto_tsquery('english', query)
        
        stmt = select(func.count()).select_from(NewsArticle).where(
            NewsArticle.is_duplicate == False,
            search_vector.op('@@')(search_query),
        )
        if category:
            stmt = stmt.where(NewsArticle.category == category)
        result = await self.session.execute(stmt)
        return result.scalar() or 0


class BookmarkRepository:
    """Bookmark data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID, article_id: UUID) -> UserBookmark:
        bookmark = UserBookmark(user_id=user_id, article_id=article_id)
        self.session.add(bookmark)
        await self.session.flush()
        return bookmark

    async def delete(self, user_id: UUID, article_id: UUID) -> bool:
        stmt = select(UserBookmark).where(
            UserBookmark.user_id == user_id,
            UserBookmark.article_id == article_id,
        )
        result = await self.session.execute(stmt)
        bookmark = result.scalar_one_or_none()
        if bookmark:
            await self.session.delete(bookmark)
            return True
        return False

    async def get_by_user(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> Sequence[UserBookmark]:
        stmt = select(UserBookmark).where(UserBookmark.user_id == user_id).options(
            selectinload(UserBookmark.article)
        ).order_by(desc(UserBookmark.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_user(self, user_id: UUID) -> int:
        stmt = select(func.count()).select_from(UserBookmark).where(UserBookmark.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def is_bookmarked(self, user_id: UUID, article_id: UUID) -> bool:
        stmt = select(func.count()).select_from(UserBookmark).where(
            UserBookmark.user_id == user_id,
            UserBookmark.article_id == article_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar() > 0


class ReadHistoryRepository:
    """Read history data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user_id: UUID, article_id: UUID) -> UserReadHistory:
        # Check if already exists
        stmt = select(UserReadHistory).where(
            UserReadHistory.user_id == user_id,
            UserReadHistory.article_id == article_id,
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            existing.read_at = datetime.now(timezone.utc)
            await self.session.flush()
            return existing
        
        history = UserReadHistory(user_id=user_id, article_id=article_id)
        self.session.add(history)
        await self.session.flush()
        return history

    async def get_by_user(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> Sequence[UserReadHistory]:
        stmt = select(UserReadHistory).where(UserReadHistory.user_id == user_id).options(
            selectinload(UserReadHistory.article)
        ).order_by(desc(UserReadHistory.read_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class RefreshLogRepository:
    """Refresh log data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self) -> RefreshLog:
        log = RefreshLog()
        self.session.add(log)
        await self.session.flush()
        return log

    async def update(
        self,
        log_id: UUID,
        completed_at: datetime | None = None,
        articles_fetched: int | None = None,
        articles_added: int | None = None,
        articles_skipped: int | None = None,
        ai_processed: int | None = None,
        ai_failed: int | None = None,
        status: str | None = None,
        error_message: str | None = None,
    ) -> RefreshLog | None:
        log = await self.session.get(RefreshLog, log_id)
        if log:
            if completed_at is not None:
                log.completed_at = completed_at
            if articles_fetched is not None:
                log.articles_fetched = articles_fetched
            if articles_added is not None:
                log.articles_added = articles_added
            if articles_skipped is not None:
                log.articles_skipped = articles_skipped
            if ai_processed is not None:
                log.ai_processed = ai_processed
            if ai_failed is not None:
                log.ai_failed = ai_failed
            if status is not None:
                log.status = status
            if error_message is not None:
                log.error_message = error_message
            await self.session.flush()
        return log

    async def get_latest(self, limit: int = 10) -> Sequence[RefreshLog]:
        stmt = select(RefreshLog).order_by(desc(RefreshLog.started_at)).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()