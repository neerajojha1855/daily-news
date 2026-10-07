import math
from uuid import UUID
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_optional_user_id
from app.db.models import NewsCategory
from app.db.repositories import NewsArticleRepository, ReadHistoryRepository, UserPreferencesRepository
from app.db.session import get_db
from app.schemas import (
    ArticleDetailResponse,
    ArticleListResponse,
    ArticleSearchResult,
    CategoryResponse
)
from app.services.recommendations import RecommendationService

router = APIRouter()

@router.get("", response_model=ArticleSearchResult, summary="List news articles", description="Fetch paginated news articles filtered by category, minimum importance score and sort others.")
async def list_news(
    category: Optional[NewsCategory] = None,
    sort: Literal["latest", "importance", "trending", "recommended"] = "latest",
    min_importance: float = Query(0.0, ge=0.0, le=1.0),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[UUID] = Depends(get_optional_user_id),
    db: AsyncSession = Depends(get_db),
) -> ArticleSearchResult:
    article_repo = NewsArticleRepository(db)
    offset = (page - 1) * page_size

    if sort == "recommended" and user_id:
        prefs_repo = UserPreferencesRepository(db)
        prefs = await prefs_repo.get_by_user_id(user_id)
        rec_service = RecommendationService(db)
        articles = await rec_service.get_personalized_feed(
            user_id=user_id, user_preferences=prefs, limit=page_size, offset=offset
        )
        total = await article_repo.count_latest(category)
    elif sort == "importance":
        articles = await article_repo.get_by_importance(
            category=category, limit=page_size, offset=offset, min_importance=min_importance
        )
        total = await article_repo.count_latest(category)
    elif sort == "trending":
        articles = await article_repo.get_trending(
            category=category, limit=page_size, offset=offset, hours=48
        )
        total = await article_repo.count_latest(category)
    else:
        articles = await article_repo.get_latest(
            category=category, limit=page_size, offset=offset, exclude_duplicates=True
        )
        total = await article_repo.count_latest(category)

    total_pages = max(1, math.ceil(total / page_size)) if total > 0 else 1

    return ArticleSearchResult(
        articles=[ArticleListResponse.model_validate(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

@router.get(
    "/trending",
    response_model=list[ArticleListResponse],
    summary="Get trending stories",
    description="Returns top trending articles calculated using 24h freshness decay and AI importance weighting.",
)
async def get_trending_news(
    limit: int = Query(10, ge=1, le=50),
    category: Optional[NewsCategory] = None,
    db: AsyncSession = Depends(get_db),
) -> list[ArticleListResponse]:
    article_repo = NewsArticleRepository(db)
    articles = await article_repo.get_trending(category=category, limit=limit, hours=24)
    return [ArticleListResponse.model_validate(a) for a in articles]


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    summary="List available categories",
    description="Returns all active news categories with article count statistics.",
)
async def list_categories(
    db: AsyncSession = Depends(get_db),
) -> list[CategoryResponse]:
    article_repo = NewsArticleRepository(db)
    categories = []
    for cat in NewsCategory:
        count = await article_repo.count_latest(category=cat)
        label = cat.value.replace("_", " ").title()
        categories.append(CategoryResponse(category=cat.value, label=label, count=count))
    return categories


@router.get(
    "/search",
    response_model=ArticleSearchResult,
    summary="Search news articles",
    description="Full-text indexed search across titles, descriptions, and article contents.",
)
async def search_news(
    q: str = Query(..., min_length=1, max_length=200, description="Search query string"),
    category: Optional[NewsCategory] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ArticleSearchResult:
    article_repo = NewsArticleRepository(db)
    offset = (page - 1) * page_size
    articles = await article_repo.search(
        query=q,
        category=category,
        limit=page_size,
        offset=offset,
    )
    total = await article_repo.count_search(query=q, category=category)
    total_pages = max(1, math.ceil(total / page_size)) if total > 0 else 1
    return ArticleSearchResult(
        articles=[ArticleListResponse.model_validate(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{article_id}",
    response_model=ArticleDetailResponse,
    summary="Get article detail",
    description="Returns full article details with AI-generated summary, topics, and entities. Asynchronously records reading history if logged in.",
)
async def get_article_detail(
    article_id: UUID,
    user_id: Optional[UUID] = Depends(get_optional_user_id),
    db: AsyncSession = Depends(get_db),
) -> ArticleDetailResponse:
    article_repo = NewsArticleRepository(db)
    article = await article_repo.get_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )
    # Asynchronously track reading history for logged-in users
    if user_id:
        history_repo = ReadHistoryRepository(db)
        await history_repo.add(user_id=user_id, article_id=article_id)
    return ArticleDetailResponse.model_validate(article)
