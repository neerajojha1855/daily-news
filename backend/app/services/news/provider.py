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


class NewsDataIOProvider(BaseNewsProvider):
    """NewsData.io provider (newsdata.io)."""

    name = "newsdata"
    
    supported_categories = [
        "top", "business", "entertainment", "health", 
        "science", "sports", "technology", "world", "politics", "environment"
    ]

    CATEGORY_MAP = {
        "technology": "technology",
        "business": "business",
        "politics": "politics",
        "science": "science",
        "health": "health",
        "sports": "sports",
        "entertainment": "entertainment",
        "world": "world",
        "india": "top",
        "education": "top",
        "environment": "environment",
    }

    def __init__(self, api_key: str, base_url: str = "https://newsdata.io/api/1"):
        super().__init__(api_key, base_url)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def close(self):
        await self.client.aclose()

    def _normalize_article(self, raw: dict) -> RawNewsArticle:
        # Newsdata.io pubDate format: "2023-01-20 15:30:00"
        pub_date_str = raw.get("pubDate")
        published_at = None
        if pub_date_str:
            try:
                published_at = datetime.strptime(pub_date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            except ValueError:
                published_at = self._parse_datetime(pub_date_str)
        
        source_name = "Unknown"
        source_id = raw.get("source_id")
        if isinstance(source_id, str):
            source_name = source_id.capitalize()

        return RawNewsArticle(
            external_id=raw.get("article_id") or raw.get("link"),
            title=raw.get("title", "").strip(),
            description=raw.get("description"),
            content=raw.get("content") or raw.get("description"),
            url=raw.get("link", ""),
            image_url=raw.get("image_url"),
            source_name=source_name,
            source_url=raw.get("source_url"),
            author=(raw.get("creator") or [None])[0] if isinstance(raw.get("creator"), list) else raw.get("creator"),
            published_at=published_at,
            category=raw.get("category", [None])[0] if isinstance(raw.get("category"), list) else None,
            language=raw.get("language", "en"),
        )

    async def _fetch(self, endpoint: str, params: dict) -> list[RawNewsArticle]:
        url = f"{self.base_url}/{endpoint}"
        params["apikey"] = self.api_key
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "error":
                raise Exception(f"NewsData error: {data.get('results', {}).get('message', 'Unknown')}")
                
            articles = data.get("results", [])
            return [self._normalize_article(a) for a in articles if a.get("title")]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid NewsData API key")
            elif e.response.status_code == 429:
                raise Exception("NewsData rate limit exceeded")
            raise Exception(f"NewsData HTTP error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise Exception(f"NewsData request failed: {str(e)}")

    async def fetch_articles(
        self,
        category: str | None = None,
        query: str | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        params = {"language": language}
        if query:
            params["q"] = query
        if category and category in self.CATEGORY_MAP:
            params["category"] = self.CATEGORY_MAP[category]
        return await self._fetch("news", params)

    async def fetch_top_headlines(
        self,
        category: str | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        return await self.fetch_articles(category, None, language, page, page_size)

    async def search_articles(
        self,
        query: str,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> list[RawNewsArticle]:
        return await self.fetch_articles(None, query, language, page, page_size)


# Provider factory
def get_news_provider(provider_name: str, api_key: str, base_url: str) -> BaseNewsProvider:
    """Get news provider instance by name."""
    providers = {
        "newsapi": NewsAPIProvider,
        "gnews": GNewsProvider,
        "newsdata": NewsDataIOProvider,
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown news provider: {provider_name}")
    
    return provider_class(api_key, base_url)