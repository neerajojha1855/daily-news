from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Article
from .serializers import ArticleSerializer

class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Article.objects.all()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

@api_view(['GET'])
def trending_articles(request):
    # Mocking trending as latest articles. Real app would factor in views/likes.
    trending = Article.objects.all().order_by('-published_at')[:10]
    serializer = ArticleSerializer(trending, many=True)
    return Response(serializer.data)
