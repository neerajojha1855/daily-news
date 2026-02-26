from django.core.management.base import BaseCommand
from articles.services import NewsFetcherService

class Command(BaseCommand):
    help = 'Fetches latest news from external APIs'

    def handle(self, *args, **options):
        fetcher = NewsFetcherService()
        categories = ['technology', 'business', 'sports', 'entertainment', 'health', 'science', 'politics', 'world']
        for cat in categories:
            self.stdout.write(f"Fetching news for {cat}...")
            articles = fetcher.process_and_save_articles(cat)
            self.stdout.write(self.style.SUCCESS(f"Saved {len(articles)} new articles for {cat}."))
