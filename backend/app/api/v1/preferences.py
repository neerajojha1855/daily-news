"""
User news preference management.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.repositories import UserPreferencesRepository
from app.db.session import get_db
from app.schemas import UserPreferencesResponse, UserPreferencesUpdate

router = APIRouter()


@router.get(
    "",
    response_model=UserPreferencesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user preferences",
    description="Retrieves the preferred categories, sources, and language for the current user.",
)
async def get_preferences(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserPreferencesResponse:
    prefs_repo = UserPreferencesRepository(db)
    prefs = await prefs_repo.get_by_user_id(user_id)
    if not prefs:
        prefs = await prefs_repo.create_or_update(user_id=user_id)
    return UserPreferencesResponse.model_validate(prefs)


@router.put(
    "",
    response_model=UserPreferencesResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user preferences",
    description="Updates preferred categories, sources, and language for personalized recommendations.",
)
async def update_preferences(
    data: UserPreferencesUpdate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserPreferencesResponse:
    prefs_repo = UserPreferencesRepository(db)
    prefs = await prefs_repo.create_or_update(
        user_id=user_id,
        preferred_categories=data.preferred_categories,
        preferred_sources=data.preferred_sources,
        preferred_language=data.preferred_language,
    )
    return UserPreferencesResponse.model_validate(prefs)
