import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from articles.models import Article
from articles.services import NewsFetcherService
import time

def backfill():
    articles = Article.objects.filter(ai_summary='Summary failed.')
    count = articles.count()
    print(f"Found {count} articles with failed summaries.")
    
    if count == 0:
        return
        
    service = NewsFetcherService()
    
    success = 0
    for i, article in enumerate(articles):
        print(f"Processing {i+1}/{count}: {article.title[:30]}...")
        content = article.content or article.description or ""
        summary = service._generate_summary(content)
        
        if summary and summary != "Summary failed.":
            article.ai_summary = summary
            article.save(update_fields=['ai_summary'])
            success += 1
        
        # Add a small delay to avoid hitting rate limits
        time.sleep(2)
        
    print(f"Successfully backfilled {success} summaries.")

if __name__ == '__main__':
    backfill()
