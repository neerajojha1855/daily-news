"""
News ingestion pipeline: fetch, normalize, deduplicate, analyze, persist.
"""
from datetime import datetime, timezone
import logging
from typing import Optional
from urllib.parse import urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import NewsArticle, NewsCategory, RefreshLog, SentimentType
from app.db.repositories import NewsArticleRepository, RefreshLogRepository
from app.services.ai.gemini import get_gemini_service
from app.services.news.provider import get_news_provider

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates the full news ingestion pipeline."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.article_repo = NewsArticleRepository(session)
        self.log_repo = RefreshLogRepository(session)
        self.gemini = get_gemini_service()
        api_key = settings.NEWS_DATA_API_KEY if settings.NEWS_API_PROVIDER == "newsdata" else settings.NEWS_API_KEY
        base_url = settings.NEWS_DATA_BASE_URL if settings.NEWS_API_PROVIDER == "newsdata" else settings.NEWS_API_BASE_URL
        
        self.news_provider = get_news_provider(
            settings.NEWS_API_PROVIDER,
            api_key,
            base_url,
        )

    def _canonicalize_url(self, url: str) -> str:
        """Create a canonical URL for deduplication by stripping tracking query params and trailing slashes."""
        try:
            parsed = urlparse(url)
            clean_path = parsed.path.rstrip("/")
            return urlunparse((
                parsed.scheme or "https",
                parsed.netloc.lower(),
                clean_path,
                "",
                "",
                "",
            ))
        except Exception:
            return url.strip().rstrip("/")

    async def run_ingestion(self, categories: Optional[list[str]] = None) -> RefreshLog:
        """Run the complete ingestion pipeline."""
        log = await self.log_repo.create()
        categories = categories or settings.NEWS_CATEGORIES

        articles_fetched = 0
        articles_added = 0
        articles_skipped = 0
        ai_processed = 0
        ai_failed = 0

        try:
            for category in categories:
                try:
                    raw_articles = await self.news_provider.fetch_top_headlines(
                        category=category,
                        language="en",
                        page=1,
                        page_size=20,
                    )
                    articles_fetched += len(raw_articles)

                    for raw in raw_articles:
                        try:
                            canonical_url = self._canonicalize_url(str(raw.url))

                            # 1. Deterministic URL deduplication check
                            if await self.article_repo.exists_by_canonical_url(canonical_url):
                                articles_skipped += 1
                                continue

                            # 2. External ID deduplication check
                            if raw.external_id:
                                existing = await self.article_repo.get_by_external_id(
                                    raw.external_id, raw.source_name
                                )
                                if existing:
                                    articles_skipped += 1
                                    continue

                            # 3. Analyze with Gemini (or deterministic fallback)
                            article_dict = {
                                "title": raw.title,
                                "description": raw.description,
                                "content": raw.content,
                                "source_name": raw.source_name,
                                "published_at": raw.published_at.isoformat() if raw.published_at else "",
                                "url": str(raw.url),
                            }

                            analysis = await self.gemini.analyze_article(article_dict)
                            ai_processed += 1

                            if not analysis.is_suitable_for_feed:
                                articles_skipped += 1
                                continue

                            # 4. Map Enums safely
                            try:
                                mapped_category = NewsCategory(analysis.category.value)
                            except Exception:
                                mapped_category = NewsCategory.OTHER

                            try:
                                mapped_sentiment = SentimentType(analysis.sentiment.value)
                            except Exception:
                                mapped_sentiment = SentimentType.NEUTRAL

                            # 5. Persist normalized article
                            article = NewsArticle(
                                external_id=raw.external_id,
                                title=raw.title,
                                description=raw.description,
                                content=raw.content,
                                url=str(raw.url),
                                canonical_url=canonical_url,
                                image_url=str(raw.image_url) if raw.image_url else None,
                                source_name=raw.source_name,
                                source_url=str(raw.source_url) if raw.source_url else None,
                                author=raw.author,
                                published_at=raw.published_at or datetime.now(timezone.utc),
                                category=mapped_category,
                                subcategory=analysis.subcategory,
                                summary=analysis.summary,
                                topics=analysis.topics,
                                entities=analysis.entities,
                                keywords=analysis.keywords,
                                sentiment=mapped_sentiment,
                                importance_score=analysis.importance_score,
                                reading_time=analysis.estimated_reading_minutes,
                                is_duplicate=analysis.is_duplicate,
                                is_featured=analysis.importance_score >= 0.85,
                                ai_processed=True,
                            )

                            await self.article_repo.create(article)
                            articles_added += 1

                        except Exception as e:
                            logger.error(f"Error processing article: {e}")
                            articles_skipped += 1
                            ai_failed += 1

                except Exception as e:
                    logger.error(f"Error fetching category {category}: {e}")
                    ai_failed += 1

            # Update final log status
            updated_log = await self.log_repo.update(
                log.id,
                completed_at=datetime.now(timezone.utc),
                articles_fetched=articles_fetched,
                articles_added=articles_added,
                articles_skipped=articles_skipped,
                ai_processed=ai_processed,
                ai_failed=ai_failed,
                status="completed",
            )
            return updated_log or log

        except Exception as e:
            logger.error(f"Ingestion run failed: {e}")
            await self.log_repo.update(
                log.id,
                completed_at=datetime.now(timezone.utc),
                status="failed",
                error_message=str(e),
            )
            raise

    async def close(self):
        if hasattr(self.news_provider, "close"):
            await self.news_provider.close()


async def run_scheduled_ingestion() -> RefreshLog:
    """Entrypoint for scheduled ingestion."""
    from app.db.session import get_db_context

    async with get_db_context() as session:
        service = IngestionService(session)
        try:
            return await service.run_ingestion()
        finally:
            await service.close()