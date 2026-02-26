from django.urls import path
from articles.api_views import ArticleListView, trending_articles
from favorites.api_views import FavoriteListCreateView, FavoriteDeleteView

urlpatterns = [
    # Articles API
    path('articles/', ArticleListView.as_view(), name='api-articles-list'),
    path('articles/trending/', trending_articles, name='api-articles-trending'),
    
    # Favorites API
    path('favorites/', FavoriteListCreateView.as_view(), name='api-favorites-create'), # POST
    path('favorites/<int:pk>/', FavoriteDeleteView.as_view(), name='api-favorites-delete'), # DELETE
    path('me/favorites/', FavoriteListCreateView.as_view(), name='api-me-favorites'), # GET
]
