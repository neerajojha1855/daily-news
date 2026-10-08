"""
NewsAPI.org provider implementation.
"""
import httpx
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import urlencode

from app.services.news.base import BaseNewsProvider, RawNewsArticle


class NewsAPIProvider(BaseNewsProvider):
    """NewsAPI.org provider (newsapi.org)."""

    name = "newsapi"
    
    supported_categories = [
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

    # Category mapping from our internal categories to NewsAPI categories
    CATEGORY_MAP = {
        "technology": "technology",
        "business": "business",
        "politics": "nation",  # NewsAPI doesn't have politics, use nation
        "science": "science",
        "health": "health",
        "sports": "sports",
        "entertainment": "entertainment",
        "world": "world",
        "india": "nation",  # Will need country=in for India-specific
        "education": "general",
        "environment": "general",
    }

    def __init__(self, api_key: str, base_url: str = "https://newsapi.org/v2"):
        super().__init__(api_key, base_url)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def close(self):
        await self.client.aclose()

    def _build_headers(self) -> dict:
        return {
            "X-Api-Key": self.api_key,
            "User-Agent": "DailyNews/1.0",
        }

    def _normalize_article(self, raw: dict) -> RawNewsArticle:
        """Normalize NewsAPI article to our standard format."""
        return RawNewsArticle(
            external_id=raw.get("url"),  # Use URL as external ID since NewsAPI doesn't provide one
            title=raw.get("title", "").strip(),
            description=raw.get("description"),
            content=raw.get("content"),
            url=raw.get("url", ""),
            image_url=raw.get("urlToImage"),
            source_name=raw.get("source", {}).get("name", "Unknown"),
            source_url=raw.get("source", {}).get("url"),
            author=raw.get("author"),
            published_at=self._parse_datetime(raw.get("publishedAt")),
            category=raw.get("category"),  # Not provided by NewsAPI in article
            language=raw.get("language", "en"),
        )

    async def _fetch(
        self,
        endpoint: str,
        params: dict,
    ) -> list[RawNewsArticle]:
        """Generic fetch method."""
        url = f"{self.base_url}/{endpoint}"
        headers = self._build_headers()
        
        try:
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            
            articles = data.get("articles", [])
            return [self._normalize_article(a) for a in articles if a.get("title")]
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid NewsAPI key")
            elif e.response.status_code == 429:
                raise Exception("NewsAPI rate limit exceeded")
            raise Exception(f"NewsAPI HTTP error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise Exception(f"NewsAPI request failed: {str(e)}")

    async def fetch_articles(
        self,
        category: str | None = None,
        query: str | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        """Fetch articles from /everything endpoint."""
        params = {
            "language": language,
            "page": page,
            "pageSize": min(page_size, 100),  # NewsAPI max is 100
        }
        
        if query:
            params["q"] = query
        if category and category in self.CATEGORY_MAP:
            params["category"] = self.CATEGORY_MAP[category]
        
        return await self._fetch("everything", params)

    async def fetch_top_headlines(
        self,
        category: str | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        """Fetch top headlines from /top-headlines endpoint."""
        params = {
            "language": language,
            "page": page,
            "pageSize": min(page_size, 100),
        }
        
        if category and category in self.CATEGORY_MAP:
            params["category"] = self.CATEGORY_MAP[category]
        
        return await self._fetch("top-headlines", params)

    async def search_articles(
        self,
        query: str,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        """Search articles using /everything endpoint."""
        params = {
            "q": query,
            "language": language,
            "page": page,
            "pageSize": min(page_size, 100),
            "sortBy": "publishedAt",
        }
        return await self._fetch("everything", params)


class GNewsProvider(BaseNewsProvider):
    """GNews.io provider (gnews.io)."""

    name = "gnews"
    
    supported_categories = [
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

    CATEGORY_MAP = {
        "technology": "technology",
        "business": "business",
        "politics": "nation",
        "science": "science",
        "health": "health",
        "sports": "sports",
        "entertainment": "entertainment",
        "world": "world",
        "india": "nation",
        "education": "general",
        "environment": "general",
    }

    def __init__(self, api_key: str, base_url: str = "https://gnews.io/api/v4"):
        super().__init__(api_key, base_url)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def close(self):
        await self.client.aclose()

    def _build_params(self, extra: dict | None = None) -> dict:
        params = {"token": self.api_key, "lang": "en", "max": 20}
        if extra:
            params.update(extra)
        return params

    def _normalize_article(self, raw: dict) -> RawNewsArticle:
        return RawNewsArticle(
            external_id=raw.get("url"),
            title=raw.get("title", "").strip(),
            description=raw.get("description"),
            content=raw.get("content"),
            url=raw.get("url", ""),
            image_url=raw.get("image"),
            source_name=raw.get("source", {}).get("name", "Unknown"),
            source_url=raw.get("source", {}).get("url"),
            author=None,  # GNews doesn't provide author
            published_at=self._parse_datetime(raw.get("publishedAt")),
            category=None,
            language="en",
        )

    async def _fetch(self, endpoint: str, params: dict) -> list[RawNewsArticle]:
        url = f"{self.base_url}/{endpoint}"
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            return [self._normalize_article(a) for a in articles if a.get("title")]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid GNews API key")
            elif e.response.status_code == 429:
                raise Exception("GNews rate limit exceeded")
            raise Exception(f"GNews HTTP error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise Exception(f"GNews request failed: {str(e)}")

    async def fetch_articles(
        self,
        category: str | None = None,
        query: str | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        params = self._build_params({
            "max": min(page_size, 20),  # GNews max is 20
            "page": page,
        })
        if query:
            params["q"] = query
        if category and category in self.CATEGORY_MAP:
            params["topic"] = self.CATEGORY_MAP[category]
        return await self._fetch("search", params)

    async def fetch_top_headlines(
        self,
        category: str | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        params = self._build_params({
            "max": min(page_size, 20),
            "page": page,
        })
        if category and category in self.CATEGORY_MAP:
            params["topic"] = self.CATEGORY_MAP[category]
        return await self._fetch("top-headlines", params)

    async def search_articles(
        self,
        query: str,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        params = self._build_params({
            "q": query,
            "max": min(page_size, 20),
            "page": page,
        })
        return await self._fetch("search", params)


# Provider factory
def get_news_provider(provider_name: str, api_key: str, base_url: str) -> BaseNewsProvider:
    """Get news provider instance by name."""
    providers = {
        "newsapi": NewsAPIProvider,
        "gnews": GNewsProvider,
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown news provider: {provider_name}")
    
    return provider_class(api_key, base_url)