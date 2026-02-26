from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
]
