"""
Recommendation service for personalized feeds.
"""
import math
from datetime import datetime, timedelta, timezone
from typing import Sequence
from uuid import UUID

from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import NewsArticle, NewsCategory, UserPreferences, UserReadHistory
from app.db.repositories import NewsArticleRepository


class RecommendationService:
    """Deterministic recommendation scoring for personalized feeds."""

    # Configurable weights
    WEIGHTS = {
        "freshness": 0.35,
        "category_match": 0.25,
        "importance": 0.20,
        "source_diversity": 0.10,
        "reading_interest": 0.10,
    }

    def __init__(self, session: AsyncSession):
        self.session = session
        self.article_repo = NewsArticleRepository(session)

    def _compute_freshness_score(self, published_at: datetime) -> float:
        """Compute freshness score (1.0 = now, 0.0 = 7+ days old)."""
        age_hours = (datetime.now(timezone.utc) - published_at).total_seconds() / 3600
        # Exponential decay: half-life ~24 hours
        return math.exp(-age_hours / 24)

    def _compute_category_score(self, article_category: NewsCategory, preferred_categories: list[str]) -> float:
        """Compute category match score."""
        if not preferred_categories:
            return 0.5  # Neutral if no preferences
        
        pref_set = set(preferred_categories)
        if article_category.value in pref_set:
            return 1.0
        
        # Partial match for related categories
        related = {
            NewsCategory.TECHNOLOGY: {"science", "business"},
            NewsCategory.BUSINESS: {"technology", "politics"},
            NewsCategory.POLITICS: {"world", "business"},
            NewsCategory.SCIENCE: {"technology", "health", "environment"},
            NewsCategory.HEALTH: {"science", "environment"},
            NewsCategory.WORLD: {"politics", "india"},
            NewsCategory.INDIA: {"world", "politics"},
        }
        
        if article_category in related:
            if pref_set & related[article_category]:
                return 0.6
        
        return 0.1  # Low but not zero

    def _compute_importance_score(self, importance: float) -> float:
        """Normalize importance (already 0-1)."""
        return importance

    def _compute_source_diversity(self, article: NewsArticle, recent_articles: Sequence[NewsArticle]) -> float:
        """Penalize too many articles from same source."""
        same_source_count = sum(1 for a in recent_articles if a.source_name == article.source_name)
        if same_source_count == 0:
            return 1.0
        elif same_source_count <= 2:
            return 0.8
        elif same_source_count <= 4:
            return 0.5
        return 0.2

    def _compute_reading_interest(
        self,
        article: NewsArticle,
        read_history: Sequence[UserReadHistory],
    ) -> float:
        """Score based on user's reading patterns."""
        if not read_history:
            return 0.5
        
        # Check topic/entity overlap with recently read articles
        recent_topics = set()
        recent_entities = set()
        for rh in read_history[:20]:  # Last 20 reads
            if rh.article:
                recent_topics.update(rh.article.topics or [])
                recent_entities.update(rh.article.entities or [])
        
        article_topics = set(article.topics or [])
        article_entities = set(article.entities or [])
        
        topic_overlap = len(article_topics & recent_topics)
        entity_overlap = len(article_entities & recent_entities)
        
        # Score based on overlap
        score = min(1.0, (topic_overlap * 0.15) + (entity_overlap * 0.1) + 0.3)
        return score

    async def score_articles(
        self,
        articles: Sequence[NewsArticle],
        user_preferences: UserPreferences | None,
        read_history: Sequence[UserReadHistory],
    ) -> list[tuple[NewsArticle, float]]:
        """Score and rank articles for a user."""
        preferred_categories = user_preferences.preferred_categories if user_preferences else []
        
        # Get recent articles for source diversity
        recent_articles = await self.article_repo.get_latest(limit=50, exclude_duplicates=True)
        
        scored = []
        for article in articles:
            freshness = self._compute_freshness_score(article.published_at)
            category_match = self._compute_category_score(article.category, preferred_categories)
            importance = self._compute_importance_score(article.importance_score)
            source_div = self._compute_source_diversity(article, recent_articles)
            reading_int = self._compute_reading_interest(article, read_history)
            
            score = (
                self.WEIGHTS["freshness"] * freshness +
                self.WEIGHTS["category_match"] * category_match +
                self.WEIGHTS["importance"] * importance +
                self.WEIGHTS["source_diversity"] * source_div +
                self.WEIGHTS["reading_interest"] * reading_int
            )
            
            scored.append((article, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    async def get_personalized_feed(
        self,
        user_id: UUID,
        user_preferences: UserPreferences | None,
        limit: int = 20,
        offset: int = 0,
    ) -> Sequence[NewsArticle]:
        """Get personalized feed for a user."""
        # Get candidate articles (recent, non-duplicate)
        candidates = await self.article_repo.get_latest(limit=100, exclude_duplicates=True)
        
        # Get user's read history
        from app.db.repositories import ReadHistoryRepository
        read_history_repo = ReadHistoryRepository(self.session)
        read_history = await read_history_repo.get_by_user(user_id, limit=50)
        
        # Score and rank
        scored = await self.score_articles(candidates, user_preferences, read_history)
        
        # Apply pagination
        paginated = scored[offset:offset + limit]
        return [article for article, _ in paginated]