"""
Security utilities: password hashing, JWT tokens, and authentication helpers.
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal, Optional
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()

# Password hashing with Argon2
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its Argon2 hash."""
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False
    except Exception:
        # Re-hash if parameters changed
        return False


# JWT Token handling
class TokenPayload(BaseModel):
    sub: str  # user_id
    email: str
    username: str
    exp: int
    iat: int
    type: Literal["access", "refresh"] = "access"


def create_access_token(
    user_id: UUID,
    email: str,
    username: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a short-lived access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "username": username,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "access",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: UUID,
    email: str,
    username: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a longer-lived refresh token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "username": username,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# FastAPI Dependencies
security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> UUID:
    """Extract and validate current user ID from access token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    if payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UUID(payload.sub)


async def get_current_user_payload(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> TokenPayload:
    """Extract and validate current user payload from access token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    if payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


# Optional authentication (for public endpoints that can benefit from user context)
async def get_optional_user_id(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> Optional[UUID]:
    """Get user ID if authenticated, otherwise None."""
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        if payload.type == "access":
            return UUID(payload.sub)
    except HTTPException:
        pass
    return None


def verify_cron_secret(request: Request) -> bool:
    """Verify the cron secret for protected internal endpoints."""
    if not settings.CRON_SECRET:
        return False
    provided = request.headers.get("X-Cron-Secret") or request.query_params.get(
        "cron_secret"
    )
    return provided == settings.CRON_SECRET


async def require_cron_secret(request: Request) -> None:
    """Dependency to require valid cron secret."""
    if not verify_cron_secret(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid cron secret"
        )