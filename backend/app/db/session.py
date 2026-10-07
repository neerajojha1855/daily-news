"""
Database session management for SQLAlchemy 2.x with async support.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

# Create async engine
# Use NullPool for serverless environments (Vercel) to avoid connection pooling issues
connect_args = {}
if settings.async_database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

is_null_pool = settings.is_production or settings.async_database_url.startswith("sqlite")

engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,
    connect_args=connect_args,
    poolclass=NullPool if is_null_pool else None,
    pool_pre_ping=True,
    **({} if is_null_pool else {"pool_recycle": 300}),
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database session (for non-FastAPI usage)."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create tables if not exist)."""
    # Import all models to ensure they're registered
    from app.db.models import Base  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()