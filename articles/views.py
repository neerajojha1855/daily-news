from django.shortcuts import render, get_object_or_404
from .models import Article
from categories.models import Category
from django.core.paginator import Paginator

def home_view(request):
    articles = Article.objects.all()
    
    # Recommendation context based on user preferences
    if request.user.is_authenticated and request.user.preferences:
        preferred_cats = request.user.preferences.get('categories', [])
        if preferred_cats:
            articles = articles.filter(category__slug__in=preferred_cats)
            
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all()
    }
    return render(request, 'articles/home.html', context)

def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(category=category)
    
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category': category,
        'categories': Category.objects.all()
    }
    return render(request, 'articles/home.html', context)

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    
    # Simple recommendation engine: related articles
    related_articles = Article.objects.filter(category=article.category).exclude(pk=article.pk)[:3]
    
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = request.user.favorites.filter(article=article).exists()
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'is_favorite': is_favorite,
    }
    return render(request, 'articles/detail.html', context)
