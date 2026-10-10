"""
Application configuration using Pydantic Settings.
All environment variables are defined here with validation.
"""
from functools import lru_cache
from typing import Literal
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # Database
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DATABASE_URL: str | None = None

    @property
    def async_database_url(self) -> str:
        """Returns asyncpg-compatible database URL."""
        if self.DATABASE_URL:
            url = str(self.DATABASE_URL)
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self._normalize_asyncpg_url(url)
        pwd = quote_plus(self.DB_PASSWORD)
        return f"postgresql+asyncpg://{self.DB_USER}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @staticmethod
    def _normalize_asyncpg_url(url: str) -> str:
        """Remove PostgreSQL URL options that asyncpg does not support."""
        parsed = urlsplit(url)
        query = [
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if key != "channel_binding"
        ]
        return urlunsplit(parsed._replace(query=urlencode(query)))

    @property
    def sync_database_url(self) -> str:
        """Returns sync psycopg2-compatible database URL (for Alembic)."""
        if self.DATABASE_URL:
            url = str(self.DATABASE_URL)
            if url.startswith("postgresql+asyncpg://"):
                return url.replace("postgresql+asyncpg://", "postgresql://", 1)
            return url
        pwd = quote_plus(self.DB_PASSWORD)
        return f"postgresql://{self.DB_USER}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # News API
    NEWS_API_KEY: str = ""
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"

    # NewsData API (newsdata.io)
    NEWS_DATA_API_KEY: str = ""
    NEWS_DATA_BASE_URL: str = "https://newsdata.io/api/1"

    NEWS_API_PROVIDER: Literal["newsapi", "gnews", "newsdata"] = "newsapi"

    # Google Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"

    # Authentication
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Session
    SESSION_SECRET: str = ""

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: list[str] = [
        FRONTEND_URL,
        "https://daily-news-orpin.vercel.app"
    ]

    # News Refresh
    NEWS_REFRESH_INTERVAL_MINUTES: int = 15
    NEWS_CATEGORIES: list[str] = Field(
        default_factory=lambda: [
            "general",
            "world",
            "nation",
            "business",
            "technology",
            "entertainment",
            "sports",
            "science",
            "health",
        ]
    )

    # Cron / Internal
    CRON_SECRET: str | None = None

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # AI Processing
    GEMINI_MAX_RETRIES: int = 2
    GEMINI_TIMEOUT_SECONDS: int = 30
    MAX_ARTICLE_CONTENT_LENGTH: int = 8000

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()