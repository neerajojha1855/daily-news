from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.bookmarks import router as bookmarks_router
from app.api.v1.health import router as health_router
from app.api.v1.internal import router as internal_router
from app.api.v1.news import router as news_router
from app.api.v1.preferences import router as preferences_router
from app.api.v1.profile import router as profile_router

api_router = APIRouter()

# Register sub-routers
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(news_router, prefix="/news", tags=["News"])
api_router.include_router(bookmarks_router, prefix="/bookmarks", tags=["Bookmarks"])
api_router.include_router(preferences_router, prefix="/preferences", tags=["Preferences"])
api_router.include_router(profile_router, prefix="/profile", tags=["Profile"])
api_router.include_router(internal_router, prefix="/internal", tags=["Internal / Maintenance"])