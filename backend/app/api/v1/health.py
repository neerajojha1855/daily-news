from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import HealthResponse

router = APIRouter()

@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Returns API status, current UTC timezone and verifies database connectivity.",
)

async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    db_status = "ok"

    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "degraded"
    
    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        timestamp=datetime.now(timezone.utc),
        version="1.0.0",
    )