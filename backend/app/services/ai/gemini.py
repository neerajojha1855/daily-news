"""
Google Gemini AI service for article analysis.
"""
import json
import logging
from typing import Optional

import google.generativeai as genai
from pydantic import ValidationError

from app.core.config import settings
from app.services.ai.prompts import ARTICLE_ANALYSIS_PROMPT
from app.services.ai.schemas import NewsAnalysis, NewsCategory, SentimentType

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        self.model_name = settings.GEMINI_MODEL_NAME or settings.GEMINI_MODEL
        self.max_retries = settings.GEMINI_MAX_RETRIES
        self.timeout = settings.GEMINI_TIMEOUT_SECONDS
        self.max_content_length = settings.MAX_ARTICLE_CONTENT_LENGTH

        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(
                    self.model_name,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                        top_p=0.8,
                        top_k=20,
                    ),
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Generative Model: {e}")
                self.model = None
        else:
            self.model = None

    def _truncate_content(self, content: str) -> str:
        if len(content) <= self.max_content_length:
            return content
        return content[:self.max_content_length] + "..."

    def _build_prompt(self, article: dict) -> str:
        title = article.get("title", "")
        description = article.get("description", "") or ""
        content = article.get("content", "") or ""
        source = article.get("source_name", "")
        published = article.get("published_at", "")

        full_text = f"Title: {title}\n"
        if description:
            full_text += f"Description: {description}\n"
        if content:
            full_text += f"Content: {self._truncate_content(content)}\n"
        full_text += f"Source: {source}\n"
        full_text += f"Published: {published}\n"

        return f"{ARTICLE_ANALYSIS_PROMPT}\n\nArticle to analyze:\n{full_text}"

    def _parse_response(self, response_text: str) -> NewsAnalysis:
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        return NewsAnalysis(**data)

    def _guess_category(self, text: str) -> NewsCategory:
        keywords = {
            NewsCategory.TECHNOLOGY: ["tech", "ai", "software", "app", "digital", "cyber", "google", "apple", "microsoft", "nvidia", "openai", "anthropic"],
            NewsCategory.BUSINESS: ["business", "market", "stock", "economy", "financial", "revenue", "profit", "bank", "inflation"],
            NewsCategory.POLITICS: ["politics", "government", "parliament", "congress", "senate", "election", "vote", "policy", "minister"],
            NewsCategory.SCIENCE: ["science", "research", "study", "discovery", "space", "nasa", "isro", "physics", "biology", "chemistry"],
            NewsCategory.HEALTH: ["health", "medical", "hospital", "disease", "vaccine", "treatment", "doctor", "medicine"],
            NewsCategory.SPORTS: ["sport", "football", "cricket", "tennis", "olympics", "match", "tournament", "champion", "league"],
            NewsCategory.ENTERTAINMENT: ["entertainment", "movie", "film", "series", "actor", "music", "album", "concert", "bollywood", "hollywood"],
            NewsCategory.WORLD: ["world", "international", "global", "foreign", "un", "diplomatic", "treaty"],
            NewsCategory.INDIA: ["india", "delhi", "mumbai", "bengaluru", "modi", "rupee"],
            NewsCategory.EDUCATION: ["education", "university", "college", "student", "school", "exam"],
            NewsCategory.ENVIRONMENT: ["climate", "environment", "carbon", "renewable", "solar", "wind", "pollution"],
        }
        scores = {cat: sum(1 for w in words if w in text) for cat, words in keywords.items()}
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return NewsCategory.OTHER

    def _create_fallback_analysis(self, article: dict) -> NewsAnalysis:
        title = (article.get("title", "") + " " + (article.get("description", "") or "")).lower()
        category = self._guess_category(title)
        content = article.get("content", "") or article.get("description", "") or ""
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)

        summary = article.get("description") or article.get("title") or "No detailed summary available."
        if len(summary) < 50:
            summary = f"Reporting on {article.get('title', 'current events')}. {summary}".strip()
        summary = summary[:500]

        return NewsAnalysis(
            summary=summary,
            category=category,
            subcategory=None,
            topics=[category.value.title()],
            entities=[article.get("source_name", "Publisher")],
            sentiment=SentimentType.NEUTRAL,
            importance_score=0.6,
            keywords=[w for w in title.split() if len(w) > 4][:8],
            estimated_reading_minutes=reading_time,
            is_duplicate=False,
            is_suitable_for_feed=True,
        )

    async def analyze_article(self, article: dict) -> NewsAnalysis:
        if not self.model:
            return self._create_fallback_analysis(article)

        prompt = self._build_prompt(article)

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.model.generate_content_async(prompt)
                if not response.text:
                    raise ValueError("Empty response from Gemini")
                return self._parse_response(response.text)
            except Exception as e:
                logger.warning(f"Gemini analysis attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    logger.info("Using deterministic fallback analysis for article.")
                    return self._create_fallback_analysis(article)

        return self._create_fallback_analysis(article)


_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service