"""
Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, StringConstraints

# Auth schemas
class RegisterRequest(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9._]+$')]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]
    confirm_password: Annotated[str, StringConstraints(min_length=8, max_length=128)]

    def passwords_match(self) -> bool:
        return self.password == self.confirm_password


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None = None

    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    preferences: "UserPreferencesResponse | None" = None


# Preferences schemas
class UserPreferencesBase(BaseModel):
    preferred_categories: list[str] = Field(default_factory=list)
    preferred_sources: list[str] = Field(default_factory=list)
    preferred_language: str = Field(default="en", min_length=2, max_length=10)


class UserPreferencesUpdate(UserPreferencesBase):
    pass


class UserPreferencesResponse(UserPreferencesBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# News article schemas
class NewsCategory(str, Enum):
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


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class ArticleBase(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    url: str
    image_url: str | None = None
    source_name: str
    source_url: str | None = None
    author: str | None = None
    published_at: datetime
    category: NewsCategory
    subcategory: str | None = None
    summary: str | None = None
    topics: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    sentiment: SentimentType
    importance_score: float = Field(ge=0, le=1)
    reading_time: int = Field(ge=1, le=60)
    is_featured: bool = False


class ArticleListResponse(ArticleBase):
    class Config:
        from_attributes = True


class ArticleDetailResponse(ArticleBase):
    content: str | None = None
    canonical_url: str | None = None
    fetched_at: datetime
    created_at: datetime
    updated_at: datetime
    is_duplicate: bool
    ai_processed: bool

    class Config:
        from_attributes = True


class ArticleSearchResult(BaseModel):
    articles: list[ArticleListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CategoryResponse(BaseModel):
    category: NewsCategory
    label: str
    count: int


# News query parameters
class NewsQueryParams(BaseModel):
    category: NewsCategory | None = None
    sort: Literal["latest", "importance", "trending", "most_read", "recommended", "relevance"] = "latest"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    min_importance: float = Field(default=0.0, ge=0, le=1)
    source: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


# Search schemas
class SearchRequest(BaseModel):
    q: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    category: NewsCategory | None = None
    sort: Literal["relevance", "latest", "importance"] = "relevance"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# Bookmark schemas
class BookmarkResponse(BaseModel):
    id: UUID
    article_id: UUID
    created_at: datetime
    article: ArticleListResponse

    class Config:
        from_attributes = True


# Refresh log schemas
class RefreshLogResponse(BaseModel):
    id: UUID
    started_at: datetime
    completed_at: datetime | None = None
    articles_fetched: int
    articles_added: int
    articles_skipped: int
    ai_processed: int
    ai_failed: int
    status: str
    error_message: str | None = None

    class Config:
        from_attributes = True


# Health check
class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "down"]
    timestamp: datetime
    version: str = "1.0.0"


# Error schemas
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail