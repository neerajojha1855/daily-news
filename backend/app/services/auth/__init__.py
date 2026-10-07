"""
Authentication service for user management.
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.repositories import UserRepository, UserPreferencesRepository
from app.schemas import RegisterRequest, TokenResponse, UserPreferencesUpdate, UserResponse


class AuthService:
    """Authentication and user management service."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.prefs_repo = UserPreferencesRepository(session)

    async def register(self, data: RegisterRequest) -> TokenResponse:
        """Register a new user."""
        if not data.passwords_match():
            raise ValueError("Passwords do not match")

        # Check uniqueness
        if await self.user_repo.exists_by_email(data.email):
            raise ValueError("Email already registered")
        
        if await self.user_repo.exists_by_username(data.username):
            raise ValueError("Username already taken")

        # Create user
        password_hash = hash_password(data.password)
        user = await self.user_repo.create(
            email=data.email.lower(),
            username=data.username.lower(),
            password_hash=password_hash,
        )

        # Create default preferences
        await self.prefs_repo.create_or_update(user.id)

        # Generate tokens
        access_token = create_access_token(user.id, user.email, user.username)
        refresh_token = create_refresh_token(user.id, user.email, user.username)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
        )

    async def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        # Update last login
        await self.user_repo.update_last_login(user.id)

        # Generate tokens
        access_token = create_access_token(user.id, user.email, user.username)
        refresh_token = create_refresh_token(user.id, user.email, user.username)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)
        if payload.type != "refresh":
            raise ValueError("Invalid token type")

        user = await self.user_repo.get_by_id(UUID(payload.sub))
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        access_token = create_access_token(user.id, user.email, user.username)
        new_refresh_token = create_refresh_token(user.id, user.email, user.username)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=30 * 60,
        )

    async def get_current_user(self, user_id: UUID) -> UserResponse | None:
        """Get current user profile."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def update_profile(
        self,
        user_id: UUID,
        username: str | None = None,
        email: str | None = None,
    ) -> UserResponse | None:
        """Update user profile."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        if username and username != user.username:
            if await self.user_repo.exists_by_username(username):
                raise ValueError("Username already taken")
            user = await self.user_repo.update_username(user_id, username)

        if email and email != user.email:
            if await self.user_repo.exists_by_email(email):
                raise ValueError("Email already registered")
            user.email = email.lower()
            user.updated_at = datetime.now(timezone.utc)
            await self.session.flush()

        return UserResponse.model_validate(user)

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Change user password."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False

        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True

    async def update_preferences(
        self,
        user_id: UUID,
        data: UserPreferencesUpdate,
    ) -> UserResponse | None:
        """Update user preferences."""
        prefs = await self.prefs_repo.create_or_update(
            user_id=user_id,
            preferred_categories=data.preferred_categories,
            preferred_sources=data.preferred_sources,
            preferred_language=data.preferred_language,
        )

        user = await self.user_repo.get_by_id(user_id)
        if user:
            # Return user with preferences
            response = UserResponse.model_validate(user)
            return response
        return None