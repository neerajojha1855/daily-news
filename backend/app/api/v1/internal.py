"""
Internal maintenance and cron ingestion endpoints.
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_cron_secret
from app.db.repositories import RefreshLogRepository
from app.db.session import get_db
from app.schemas import RefreshLogResponse
from app.services.ingestion import IngestionService

router = APIRouter()


@router.post(
    "/refresh-news",
    response_model=RefreshLogResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_cron_secret)],
    summary="Trigger news ingestion",
    description="Protected endpoint for Vercel Cron or manual admin trigger. Fetches new articles, deduplicates, enriches with Gemini AI, and records metrics.",
)
async def trigger_news_refresh(
    db: AsyncSession = Depends(get_db),
) -> RefreshLogResponse:
    ingestion_service = IngestionService(db)
    try:
        log = await ingestion_service.run_ingestion()
        return RefreshLogResponse.model_validate(log)
    finally:
        await ingestion_service.close()


@router.get(
    "/refresh-logs",
    response_model=list[RefreshLogResponse],
    dependencies=[Depends(require_cron_secret)],
    summary="Get recent ingestion logs",
    description="Returns the execution history of recent news ingestion jobs.",
)
async def get_refresh_logs(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[RefreshLogResponse]:
    log_repo = RefreshLogRepository(db)
    logs = await log_repo.get_latest(limit=limit)
    return [RefreshLogResponse.model_validate(log) for log in logs]
