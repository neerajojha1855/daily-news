from rest_framework import serializers
from .models import Article
from categories.models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ArticleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'description', 'content', 'source', 'author', 'url', 'image_url', 'published_at', 'category', 'ai_summary', 'tags']
