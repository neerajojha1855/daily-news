from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter()

@router.post("/register",response_model=TokenResponse,status_code=status.HTTP_201_CREATED,summary="Register new user",description="Registers a new user with email, unique username and password. Returns access and refresh JWT tokens.",)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    auth_service = AuthService(db)

    try:
        return await auth_service.register(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK, summary="User login",description="Authenticates user credentials and returns new JWT access and refresh tokens.")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    auth_service = AuthService(db)

    try:
        return await auth_service.login(email=data.email, password=data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK, summary="Refresh access token",description="Exchange a valid refresh token for a fresh access token pair.")
async def refresh_tokens(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    auth_service = AuthService(db)

    try:
        return await auth_service.refresh_tokens(data.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK, summary="Get current user", description="Returns the profile information of the currently authenticated user.")
async def get_me(user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> UserResponse:
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

@router.get("/check-username", summary="Check username availability", description="Checks whether a given username is available for registration without exposing private account details.")
async def check_username(username: str = Query(..., min_length=3, max_length=30, regex=r"^[a-zA-Z0-9._]+$"), db: AsyncSession = Depends(get_db)) -> dict:
    from app.db.repositories import UserRepository
    user_repo = UserRepository(db)
    exists = await user_repo.exists_by_username(username)

    return {
        "username": username,
        "available": not exists
    }