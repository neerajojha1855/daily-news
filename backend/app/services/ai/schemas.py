"""
Pydantic schemas for AI analysis output validation.
"""
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, field_validator


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


class NewsAnalysis(BaseModel):
    """Structured output from Gemini analysis."""
    summary: str = Field(min_length=50, max_length=500)
    category: NewsCategory
    subcategory: str | None = Field(default=None, max_length=100)
    topics: list[str] = Field(default_factory=list, max_length=10)
    entities: list[str] = Field(default_factory=list, max_length=15)
    sentiment: SentimentType
    importance_score: float = Field(ge=0.0, le=1.0)
    keywords: list[str] = Field(default_factory=list, max_length=15)
    estimated_reading_minutes: int = Field(ge=1, le=60)
    is_duplicate: bool = False
    is_suitable_for_feed: bool = True

    @field_validator("topics", "entities", "keywords", mode="before")
    @classmethod
    def deduplicate_lists(cls, v: list[str]) -> list[str]:
        if not isinstance(v, list):
            return []
        # Deduplicate case-insensitively, preserve order
        seen = set()
        result = []
        for item in v:
            if isinstance(item, str):
                normalized = item.strip().lower()
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    result.append(item.strip())
        return result

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Summary cannot be empty")
        return v.strip()

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v: str | NewsCategory) -> NewsCategory:
        if isinstance(v, NewsCategory):
            return v
        if isinstance(v, str):
            val = v.strip().lower()
            try:
                return NewsCategory(val)
            except ValueError:
                return NewsCategory.OTHER
        return NewsCategory.OTHER


class BatchNewsAnalysis(BaseModel):
    """Batch analysis for multiple articles."""
    articles: list[NewsAnalysis] = Field(min_length=1, max_length=20)