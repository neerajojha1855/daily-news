"""
News provider abstraction and models.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class RawNewsArticle(BaseModel):
    """Normalized representation of a raw news article from any provider."""
    external_id: str | None = None
    title: str
    description: str | None = None
    content: str | None = None
    url: HttpUrl
    image_url: HttpUrl | None = None
    source_name: str
    source_url: HttpUrl | None = None
    author: str | None = None
    published_at: datetime
    category: str | None = None  # Provider-specific category
    language: str = "en"


class NewsProvider(Protocol):
    """Protocol for news providers."""
    
    @property
    def name(self) -> str:
        ...

    @property
    def supported_categories(self) -> list[str]:
        ...

    async def fetch_articles(
        self,
        category: str | None = None,
        query: str | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        ...

    async def fetch_top_headlines(
        self,
        category: str | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        ...

    async def search_articles(
        self,
        query: str,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        ...


class BaseNewsProvider(ABC):
    """Base class for news providers with common functionality."""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def supported_categories(self) -> list[str]:
        pass

    @abstractmethod
    async def fetch_articles(
        self,
        category: str | None = None,
        query: str | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        pass

    @abstractmethod
    async def fetch_top_headlines(
        self,
        category: str | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        pass

    @abstractmethod
    async def search_articles(
        self,
        query: str,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        pass

    def _normalize_article(self, raw: dict) -> RawNewsArticle:
        """Override in subclass to normalize provider-specific response."""
        raise NotImplementedError

    def _parse_datetime(self, value: str | None) -> datetime:
        """Parse ISO datetime string."""
        if not value:
            return datetime.now()
        try:
            # Handle various formats
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"
            return datetime.fromisoformat(value)
        except Exception:
            return datetime.now()