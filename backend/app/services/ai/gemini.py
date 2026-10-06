"""
Google Gemini AI service for article analysis.
"""
import json
import logging
from typing import Optional

import google.generativeai as genai
from pydantic import ValidationError

from app.core.config import get_settings
from app.services.ai.schemas import NewsAnalysis, NewsCategory, SentimentType

settings = get_settings()
logger = logging.getLogger(__name__)


# System prompt for article analysis
ARTICLE_ANALYSIS_PROMPT = """
You are an expert news analyst. Analyze the provided news article and extract structured information.

Return ONLY a valid JSON object matching this exact schema:
{
  "summary": "string (50-500 chars) - concise summary of the article",
  "category": "string - one of: technology, business, politics, science, health, sports, entertainment, world, india, education, environment, other",
  "subcategory": "string or null - specific subtopic (e.g., 'artificial intelligence', 'stock market', 'climate change')",
  "topics": ["string"] - up to 10 key topics/themes",
  "entities": ["string"] - up to 15 named entities (people, organizations, locations)",
  "sentiment": "string - one of: positive, neutral, negative, mixed",
  "importance_score": "number (0.0-1.0) - news importance/impact",
  "keywords": ["string"] - up to 15 relevant keywords",
  "estimated_reading_minutes": "integer (1-60) - estimated reading time",
  "is_duplicate": "boolean - whether this appears to be a duplicate/redundant story",
  "is_suitable_for_feed": "boolean - whether suitable for main news feed"
}

Guidelines:
- summary: Extract key facts, not opinions. No clickbait.
- category: Choose the single best fit from the enum.
- subcategory: More specific than category, or null.
- topics: High-level themes (e.g., ["AI regulation", "tech policy"]).
- entities: Specific names (e.g., ["OpenAI", "Sam Altman", "EU"]).
- sentiment: Overall tone of the article.
- importance_score: 0.0=trivial, 0.5=moderate, 1.0=breaking/major impact.
- keywords: Search-relevant terms.
- estimated_reading_minutes: Based on content length (avg 200 wpm).
- is_duplicate: True if content appears substantially similar to other recent stories.
- is_suitable_for_feed: False for spam, paywalls, non-news, or very low quality.

Only use information from the article. Do not hallucinate.
"""

ARTICLE_ANALYSIS_PROMPT_VERSION = "v1"


class GeminiService:
    """Service for analyzing news articles with Google Gemini."""

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL_NAME
        self.max_retries = settings.GEMINI_MAX_RETRIES
        self.timeout = settings.GEMINI_TIMEOUT_SECONDS
        self.max_content_length = settings.MAX_ARTICLE_CONTENT_LENGTH
        
        # Configure Gemini
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

    def _truncate_content(self, content: str) -> str:
        """Truncate content to max length."""
        if len(content) <= self.max_content_length:
            return content
        return content[:self.max_content_length] + "..."

    def _build_prompt(self, article: dict) -> str:
        """Build the analysis prompt for a single article."""
        title = article.get("title", "")
        description = article.get("description", "") or ""
        content = article.get("content", "") or ""
        source = article.get("source_name", "")
        published = article.get("published_at", "")
        
        # Combine available text
        full_text = f"Title: {title}\n"
        if description:
            full_text += f"Description: {description}\n"
        if content:
            full_text += f"Content: {self._truncate_content(content)}\n"
        full_text += f"Source: {source}\n"
        full_text += f"Published: {published}\n"
        
        return f"{ARTICLE_ANALYSIS_PROMPT}\n\nArticle to analyze:\n{full_text}"

    def _parse_response(self, response_text: str) -> NewsAnalysis:
        """Parse and validate Gemini response."""
        try:
            data = json.loads(response_text)
            return NewsAnalysis(**data)
        except json.JSONDecodeError as e:
            logger.warning(f"Gemini returned invalid JSON: {e}")
            raise ValidationError("Invalid JSON from Gemini")
        except ValidationError as e:
            logger.warning(f"Gemini response failed validation: {e}")
            raise

    def _create_fallback_analysis(self, article: dict) -> NewsAnalysis:
        """Create a fallback analysis when Gemini fails."""
        # Simple heuristic category detection
        title = (article.get("title", "") + " " + article.get("description", "")).lower()
        category = self._guess_category(title)
        
        word_count = len((article.get("content", "") or "").split())
        reading_time = max(1, word_count // 200)
        
        return NewsAnalysis(
            summary=article.get("description") or article.get("title") or "No summary available",
            category=category,
            subcategory=None,
            topics=[],
            entities=[],
            sentiment=SentimentType.NEUTRAL,
            importance_score=0.5,
            keywords=[],
            estimated_reading_minutes=reading_time,
            is_duplicate=False,
            is_suitable_for_feed=True,
        )

    def _guess_category(self, text: str) -> NewsCategory:
        """Simple keyword-based category guessing."""
        keywords = {
            NewsCategory.TECHNOLOGY: ["tech", "ai", "software", "app", "digital", "cyber", "startup", "silicon valley", "google", "apple", "microsoft", "amazon", "meta"],
            NewsCategory.BUSINESS: ["business", "market", "stock", "economy", "financial", "investment", "bank", "revenue", "profit", "earnings", "ipo", "merger"],
            NewsCategory.POLITICS: ["politics", "government", "parliament", "congress", "senate", "election", "vote", "policy", "minister", "president", "prime minister"],
            NewsCategory.SCIENCE: ["science", "research", "study", "scientist", "discovery", "space", "nasa", "physics", "biology", "chemistry"],
            NewsCategory.HEALTH: ["health", "medical", "hospital", "disease", "virus", "vaccine", "treatment", "doctor", "patient", "covid", "cancer"],
            NewsCategory.SPORTS: ["sport", "football", "cricket", "tennis", "olympics", "match", "tournament", "champion", "league", "team", "player"],
            NewsCategory.ENTERTAINMENT: ["entertainment", "movie", "film", "actor", "actress", "celebrity", "music", "album", "concert", "hollywood", "bollywood"],
            NewsCategory.WORLD: ["world", "international", "global", "foreign", "country", "nation", "war", "conflict", "diplomatic", "un", "eu"],
            NewsCategory.INDIA: ["india", "indian", "delhi", "mumbai", "bangalore", "modi", "rupee", "lok sabha", "rajya sabha"],
            NewsCategory.EDUCATION: ["education", "university", "college", "student", "school", "exam", "degree", "campus", "academic"],
            NewsCategory.ENVIRONMENT: ["climate", "environment", "carbon", "emission", "renewable", "solar", "wind", "pollution", "sustainability", "green"],
        }
        
        scores = {}
        for cat, words in keywords.items():
            scores[cat] = sum(1 for w in words if w in text)
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return NewsCategory.OTHER

    async def analyze_article(self, article: dict) -> NewsAnalysis:
        """Analyze a single article with retry logic."""
        prompt = self._build_prompt(article)
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.model.generate_content_async(prompt)
                
                if not response.text:
                    raise ValueError("Empty response from Gemini")
                
                return self._parse_response(response.text)
                
            except ValidationError:
                if attempt < self.max_retries:
                    logger.info(f"Retrying Gemini analysis (attempt {attempt + 2})")
                    continue
                logger.error("Gemini validation failed after retries, using fallback")
                return self._create_fallback_analysis(article)
                
            except Exception as e:
                logger.error(f"Gemini analysis error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries:
                    continue
                return self._create_fallback_analysis(article)
        
        return self._create_fallback_analysis(article)

    async def analyze_batch(self, articles: list[dict]) -> list[NewsAnalysis]:
        """Analyze multiple articles sequentially (batch API not used for simplicity)."""
        results = []
        for article in articles:
            analysis = await self.analyze_article(article)
            results.append(analysis)
        return results


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service singleton."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service