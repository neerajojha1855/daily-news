"""
News ingestion pipeline: fetch, normalize, deduplicate, analyze, persist.
"""
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import NewsArticle, NewsCategory, RefreshLog, SentimentType
from app.db.repositories import NewsArticleRepository, RefreshLogRepository
from app.services.ai.gemini import get_gemini_service
from app.services.ai.schemas import NewsAnalysis
from app.services.news.base import RawNewsArticle
from app.services.news.provider import get_news_provider

settings = get_settings()
logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates the full news ingestion pipeline."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.article_repo = NewsArticleRepository(session)
        self.log_repo = RefreshLogRepository(session)
        self.gemini = get_gemini_service()
        self.news_provider = get_news_provider(
            settings.NEWS_API_PROVIDER,
            settings.NEWS_API_KEY,
            settings.NEWS_API_BASE_URL,
        )

    async def run_ingestion(self, categories: Optional[list[str]] = None) -> RefreshLog:
        """Run the complete ingestion pipeline."""
        log = await self.log_repo.create()
        categories = categories or settings.NEWS_CATEGORIES
        
        try:
            articles_fetched = 0
            articles_added = 0
            articles_skipped = 0
            ai_processed = 0
            ai_failed = 0

            for category in categories:
                try:
                    # Fetch articles for this category
                    raw_articles = await self.news_provider.fetch_top_headlines(
                        category=category,
                        language="en",
                        page=1,
                        page_size=20,
                    )
                    articles_fetched += len(raw_articles)

                    # Process each article
                    for raw in raw_articles:
                        try:
                            # Normalize & deduplicate
                            canonical_url = self._canonicalize_url(str(raw.url))
                            
                            # Check if already exists
                            existing = await self.article_repo.get_by_canonical_url(canonical_url)
                            if existing:
                                articles_skipped += 1
                                continue

                            # Check by external ID + source
                            if raw.external_id:
                                existing = await self.article_repo.get_by_external_id(
                                    raw.external_id, raw.source_name
                                )
                                if existing:
                                    articles_skipped += 1
                                    continue

                            # Analyze with Gemini
                            article_dict = raw.model_dump()
                            article_dict["url"] = str(raw.url)
                            if raw.image_url:
                                article_dict["image_url"] = str(raw.image_url)
                            if raw.source_url:
                                article_dict["source_url"] = str(raw.source_url)
                            if raw.published_at:
                                article_dict["published_at"] = raw.published_at.isoformat()

                            analysis = await self.gemini.analyze_article(article_dict)
                            ai_processed += 1

                            if not analysis.is_suitable_for_feed:
                                articles_skipped += 1
                                continue

                            # Create article record
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
                                published_at=raw.published_at,
                                category=analysis.category,
                                subcategory=analysis.subcategory,
                                summary=analysis.summary,
                                topics=analysis.topics,
                                entities=analysis.entities,
                                keywords=analysis.keywords,
                                sentiment=analysis.sentiment,
                                importance_score=analysis.importance_score,
                                reading_time=analysis.estimated_reading_minutes,
                                is_duplicate=analysis.is_duplicate,
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

            # Update log
            await self.log_repo.update(
                log.id,
                completed_at=datetime.now(timezone.utc),
                articles_fetched=articles_fetched,
                articles_added=articles_added,
                articles_skipped=articles_skipped,
                ai_processed=ai_processed,
                ai_failed=ai_failed,
                status="completed",
            )

            logger.info(f"Ingestion completed: {articles_added} added, {articles_skipped} skipped")
            return await self.log_repo.update(log.id, status="completed")

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            await self.log_repo.update(
                log.id,
                completed_at=datetime.now(timezone.utc),
                status="failed",
                error_message=str(e),
            )
            raise

    def _canonicalize_url(self, url: str) -> str:
        """Create a canonical URL for deduplication."""
        # Remove query parameters, fragments, normalize
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        # Remove tracking parameters
        clean_query = ""
        return urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            "",
            clean_query,
            "",
        ))

    async def close(self):
        """Close provider connections."""
        if hasattr(self.news_provider, "close"):
            await self.news_provider.close()


async def run_scheduled_ingestion() -> RefreshLog:
    """Entry point for scheduled ingestion (e.g., Vercel Cron)."""
    from app.db.session import get_db_context
    
    async with get_db_context() as session:
        service = IngestionService(session)
        try:
            return await service.run_ingestion()
        finally:
            await service.close()