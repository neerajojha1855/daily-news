"""
User profile management routes.
"""
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, StringConstraints
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.repositories import BookmarkRepository, UserRepository
from app.db.session import get_db
from app.schemas import UserResponse
from app.services.auth import AuthService

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    username: Annotated[str | None, StringConstraints(min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9._]+$")] = None
    email: EmailStr | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


@router.get(
    "",
    summary="Get user profile and statistics",
    description="Returns user details along with activity statistics such as total bookmarks count.",
)
async def get_profile(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    bookmark_repo = BookmarkRepository(db)
    total_bookmarks = await bookmark_repo.count_by_user(user_id)

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
        "stats": {
            "total_bookmarks": total_bookmarks,
        },
    }


@router.put(
    "",
    response_model=UserResponse,
    summary="Update profile details",
    description="Updates username or email with uniqueness validation.",
)
async def update_profile(
    data: UpdateProfileRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    auth_service = AuthService(db)
    try:
        updated = await auth_service.update_profile(
            user_id=user_id,
            username=data.username,
            email=data.email,
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Verifies the current password and hashes the new password with Argon2.",
)
async def change_password(
    data: ChangePasswordRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_service = AuthService(db)
    try:
        success = await auth_service.change_password(
            user_id=user_id,
            current_password=data.current_password,
            new_password=data.new_password,
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
