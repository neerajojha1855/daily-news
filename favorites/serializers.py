from rest_framework import serializers
from .models import Favorite
from articles.serializers import ArticleSerializer

class FavoriteSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)
    article_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'article', 'article_id', 'saved_at']

    def create(self, validated_data):
        user = self.context['request'].user
        article_id = validated_data.pop('article_id')
        favorite, _ = Favorite.objects.get_or_create(user=user, article_id=article_id, **validated_data)
        return favorite
