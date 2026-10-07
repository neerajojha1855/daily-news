"""
Bookmarks endpoints for saving and managing user articles.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.repositories import BookmarkRepository, NewsArticleRepository
from app.db.session import get_db
from app.schemas import ArticleListResponse, BookmarkResponse

router = APIRouter()


@router.get(
    "",
    response_model=list[BookmarkResponse],
    summary="List saved bookmarks",
    description="Returns a paginated list of articles bookmarked by the current authenticated user.",
)
async def list_bookmarks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[BookmarkResponse]:
    bookmark_repo = BookmarkRepository(db)
    offset = (page - 1) * page_size
    bookmarks = await bookmark_repo.get_by_user(user_id=user_id, limit=page_size, offset=offset)

    results = []
    for b in bookmarks:
        if b.article:
            results.append(
                BookmarkResponse(
                    id=b.id,
                    article_id=b.article_id,
                    created_at=b.created_at,
                    article=ArticleListResponse.model_validate(b.article),
                )
            )
    return results


@router.post(
    "/{article_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Bookmark an article",
    description="Saves an article to the user's bookmarks list.",
)
async def add_bookmark(
    article_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    article_repo = NewsArticleRepository(db)
    article = await article_repo.get_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    bookmark_repo = BookmarkRepository(db)
    already_saved = await bookmark_repo.is_bookmarked(user_id=user_id, article_id=article_id)
    if not already_saved:
        await bookmark_repo.create(user_id=user_id, article_id=article_id)

    return {"message": "Article bookmarked successfully", "article_id": str(article_id)}


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove a bookmark",
    description="Removes an article from the user's bookmarks.",
)
async def remove_bookmark(
    article_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    bookmark_repo = BookmarkRepository(db)
    deleted = await bookmark_repo.delete(user_id=user_id, article_id=article_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )
    return {"message": "Bookmark removed successfully", "article_id": str(article_id)}


@router.get(
    "/check/{article_id}",
    summary="Check bookmark status",
    description="Checks whether a given article is bookmarked by the current user.",
)
async def check_bookmark_status(
    article_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    bookmark_repo = BookmarkRepository(db)
    is_saved = await bookmark_repo.is_bookmarked(user_id=user_id, article_id=article_id)
    return {"article_id": str(article_id), "bookmarked": is_saved}
