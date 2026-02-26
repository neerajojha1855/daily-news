import os
import requests
from google import genai
from datetime import datetime
from django.utils import timezone
from .models import Article
from categories.models import Category

class NewsFetcherService:
    def __init__(self):
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        
        if self.gemini_key:
            self.client = genai.Client(api_key=self.gemini_key)
        else:
            self.client = None

    def fetch_top_headlines(self, category_name='technology'):
        """Fetches top headlines for a given category."""
        if not self.news_api_key:
            return self._get_mock_data(category_name)
            
        url = f"https://newsapi.org/v2/top-headlines?category={category_name}&language=en&apiKey={self.news_api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json().get('articles', [])
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
            
    def _get_mock_data(self, category_name):
        return [
            {
                "title": f"Mock {category_name.capitalize()} News {i}",
                "description": "This is a mock description because no NEWS_API_KEY was provided.",
                "content": f"Full mock content for article {i}. AI should summarize this nicely if not mocked.",
                "url": f"https://example.com/mock-{category_name}-news-{i}",
                "urlToImage": "https://via.placeholder.com/800x400/0b1c24/1fd6ff?text=News+Mock",
                "publishedAt": timezone.now().isoformat(),
                "source": {"name": "MockSource"},
                "author": "Mock Author"
            } for i in range(1, 5)
        ]

    def _generate_summary(self, content):
        if not self.client or not content:
            return "AI Summary not available. Please provide GEMINI_API_KEY."
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"Summarize this news article in 2 sentences:\n\n{content}"
            )
            return response.text
        except Exception as e:
            print(f"Error summarizing content: {e}")
            return "Summary failed."

    def process_and_save_articles(self, category_name='technology'):
        articles_data = self.fetch_top_headlines(category_name)
        category_obj, _ = Category.objects.get_or_create(
            name=category_name.capitalize(), 
            defaults={'slug': category_name.lower()}
        )
        
        saved_articles = []
        for item in articles_data:
            url = item.get('url')
            if not url or Article.objects.filter(url=url).exists():
                continue # Deduplication logic
                
            # Parse date
            pub_date_str = item.get('publishedAt')
            try:
                published_at = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
            except:
                published_at = timezone.now()
                
            content = item.get('content') or item.get('description') or ""
            summary = self._generate_summary(content)
            
            article = Article.objects.create(
                title=(item.get('title') or 'Untitled')[:500],
                description=item.get('description'),
                content=content,
                source=item.get('source', {}).get('name'),
                author=item.get('author'),
                url=url,
                image_url=item.get('urlToImage'),
                published_at=published_at,
                category=category_obj,
                ai_summary=summary,
                tags=category_name.lower()
            )
            saved_articles.append(article)
            
        return saved_articles
