from django.db import models
from categories.models import Category

class Article(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=200, blank=True, null=True)
    author = models.CharField(max_length=200, blank=True, null=True)
    url = models.URLField(max_length=2000, unique=True)
    image_url = models.URLField(max_length=2000, blank=True, null=True)
    published_at = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    ai_summary = models.TextField(blank=True, null=True, help_text="AI generated summary")
    
    # Tags for recommendation
    tags = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-published_at']
