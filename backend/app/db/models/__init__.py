"""
Database models using SQLAlchemy 2.x Declarative style.
"""
import enum
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class NewsCategory(str, enum.Enum):
    """News categories enum."""

    TECHNOLOGY = "technology"
    BUSINESS = "business"
    POLITICS = "politics"
    SCIENCE = "science"
    HEALTH = "health"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    WORLD = "world"
    INDIA = "india"
    EDUCATION = "education"
    ENVIRONMENT = "environment"
    OTHER = "other"


class SentimentType(str, enum.Enum):
    """Sentiment types enum."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    preferences: Mapped["UserPreferences"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    bookmarks: Mapped[list["UserBookmark"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    read_history: Mapped[list["UserReadHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_users_email_lower", func.lower(email), unique=True),
        Index("ix_users_username_lower", func.lower(username), unique=True),
    )


class UserPreferences(Base):
    """User preferences for personalized feed."""

    __tablename__ = "user_preferences"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    preferred_categories: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    preferred_sources: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="preferences")


class NewsArticle(Base):
    """News article model."""

    __tablename__ = "news_articles"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    canonical_url: Mapped[str | None] = mapped_column(String(1000), nullable=True, unique=True, index=True)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # AI-enriched fields
    category: Mapped[NewsCategory] = mapped_column(
        Enum(NewsCategory), default=NewsCategory.OTHER, nullable=False, index=True
    )
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    topics: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    entities: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    sentiment: Mapped[SentimentType] = mapped_column(
        Enum(SentimentType), default=SentimentType.NEUTRAL, nullable=False
    )
    importance_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False, index=True)
    reading_time: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # minutes

    # Flags
    is_duplicate: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    is_featured: Mapped[bool] = mapped_column(default=False, nullable=False)
    ai_processed: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    bookmarks: Mapped[list["UserBookmark"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    read_history: Mapped[list["UserReadHistory"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_news_articles_published_at_desc", published_at.desc()),
        Index("ix_news_articles_category_published", category, published_at.desc()),
        Index("ix_news_articles_importance_published", importance_score.desc(), published_at.desc()),
        Index("ix_news_articles_source_published", source_name, published_at.desc()),
        UniqueConstraint("canonical_url", name="uq_news_articles_canonical_url"),
    )


class UserBookmark(Base):
    """User bookmarks for articles."""

    __tablename__ = "user_bookmarks"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    article_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="bookmarks")
    article: Mapped["NewsArticle"] = relationship(back_populates="bookmarks")

    __table_args__ = (
        UniqueConstraint("user_id", "article_id", name="uq_user_bookmarks_user_article"),
    )


class UserReadHistory(Base):
    """User reading history."""

    __tablename__ = "user_read_history"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    article_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="read_history")
    article: Mapped["NewsArticle"] = relationship(back_populates="read_history")

    __table_args__ = (
        Index("ix_user_read_history_user_read_at", user_id, read_at.desc()),
    )


class RefreshLog(Base):
    """News ingestion refresh logs."""

    __tablename__ = "refresh_logs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    articles_fetched: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    articles_added: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    articles_skipped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ai_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ai_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="running", nullable=False)  # running, completed, failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_refresh_logs_started_at_desc", started_at.desc()),
    )