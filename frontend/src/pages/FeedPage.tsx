import { useEffect, useMemo, useState, useTransition } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArticleCard } from "../components/news/ArticleCard";
import { ArticleDetailModal } from "../components/news/ArticleDetailModal";
import { CategoryNav } from "../components/news/CategoryNav";
import { DailyBriefingHero } from "../components/news/DailyBriefingHero";
import { TrendingSidebar } from "../components/news/TrendingSidebar";
import { Button } from "../components/ui/Button";
import { useToast } from "../context/ToastContext";
import { newsApi } from "../services/api/news";
import type { NewsArticle, NewsCategory } from "../types/news";
import { NotFoundPage } from "./NotFoundPage";

const CATEGORIES: NewsCategory[] = [
  "technology", "business", "politics", "health", "science", "world",
  "india", "education", "environment", "sports", "entertainment", "other",
];

const categoryLabels: Record<NewsCategory, string> = {
  technology: "Technology",
  business: "Business",
  politics: "Politics",
  health: "Health",
  science: "Science",
  world: "World",
  india: "India",
  education: "Education",
  environment: "Environment",
  sports: "Sports",
  entertainment: "Entertainment",
  other: "Other",
};

interface FeedPageProps {
  mode?: "latest" | "recommended";
}

export function FeedPage({ mode = "latest" }: FeedPageProps) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { slug } = useParams<{ slug?: string }>();
  const category = CATEGORIES.includes(slug as NewsCategory) ? slug as NewsCategory : undefined;
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [trending, setTrending] = useState<NewsArticle[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    startTransition(() => {
      setIsLoading(true);
      setError(null);
    });

    Promise.all([
      newsApi.getArticles({ category, sort: mode, page: 1, pageSize: 20 }),
      newsApi.getTrending(5),
    ])
      .then(([feed, trendingArticles]) => {
        if (cancelled) return;
        setArticles(feed.items);
        setTrending(trendingArticles.length > 0 ? trendingArticles : feed.items.slice(0, 5));
      })
      .catch((requestError: { message?: string }) => {
        if (!cancelled) setError(requestError.message || "We couldn't load the news feed.");
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [category, mode]);

  const title = useMemo(() => {
    if (mode === "recommended") return "Stories selected for you";
    if (category) return `${categoryLabels[category]} news`;
    return "Top stories";
  }, [category, mode]);

  const handleCategorySelect = (nextCategory: NewsCategory | "all") => {
    navigate(nextCategory === "all" ? "/" : `/category/${nextCategory}`);
  };

  const handleBookmarkToggle = async (articleId: string, isBookmarked: boolean): Promise<boolean> => {
    if (!localStorage.getItem("daily_news_token")) {
      showToast("Sign in to save stories to your reading list.", "info");
      navigate("/login", { state: { from: window.location.pathname } });
      return false;
    }

    try {
      if (isBookmarked) {
        await newsApi.addBookmark(articleId);
        showToast("Story saved to your bookmarks.", "success");
      } else {
        await newsApi.removeBookmark(articleId);
        showToast("Story removed from your bookmarks.", "info");
      }
    } catch (requestError) {
      showToast((requestError as { message?: string }).message || "We couldn't update that bookmark.", "error");
    return false;
    }
    return true;
  };

  if (slug && !category) return <NotFoundPage />;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <DailyBriefingHero
        briefing={{
          date: new Date().toISOString(),
          headline_summary: category
            ? `Stay informed with the latest ${categoryLabels[category].toLowerCase()} stories, summarized for a faster read.`
            : "A calm, concise view of the stories shaping the day.",
          top_stories: articles.slice(0, 3),
          market_pulse: mode === "recommended"
            ? "Your feed will become more personal as you read and save stories."
            : undefined,
        }}
      />

      <CategoryNav categories={CATEGORIES} activeCategory={category || "all"} onSelect={handleCategorySelect} />

      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-accent">
            {mode === "recommended" ? "Personalized feed" : "Latest coverage"}
          </p>
          <h1 className="mt-1 font-serif text-3xl font-bold text-foreground">{title}</h1>
        </div>
        {!localStorage.getItem("daily_news_token") && mode === "recommended" && (
          <Button variant="outline" size="sm" onClick={() => navigate("/login")}>Sign in for better picks</Button>
        )}
      </div>

      {error && (
        <div className="brutal-panel mb-8 bg-[#ffc3b5] p-6 text-foreground">
          <h2 className="font-semibold">The feed is temporarily unavailable</h2>
          <p className="mt-1 text-sm opacity-80">{error}</p>
          <Button className="mt-4" size="sm" onClick={() => window.location.reload()}>Try again</Button>
        </div>
      )}

      <div className="flex flex-col gap-8 lg:flex-row">
        <section className="min-w-0 flex-1" aria-labelledby="feed-heading">
          <h2 id="feed-heading" className="sr-only">{title}</h2>
          {isLoading || isPending ? (
            <div className="grid grid-cols-1 gap-7 md:grid-cols-2">
              {[1, 2, 3, 4].map((item) => <div key={item} className="h-96 animate-pulse rounded-2xl bg-surface-elevated" />)}
            </div>
          ) : articles.length === 0 ? (
            <div className="brutal-panel border-dashed bg-surface p-12 text-center shadow-none">
              <h2 className="font-serif text-2xl font-bold text-foreground">No stories here yet</h2>
              <p className="mx-auto mt-2 max-w-md text-sm text-foreground-muted">Try another category or return to the top stories feed.</p>
              <Button className="mt-5" onClick={() => navigate("/")}>Browse top stories</Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-7 md:grid-cols-2">
              {articles.map((article, index) => (
                <ArticleCard
                  key={article.id}
                  article={article}
                  featured={index === 0}
                  onClick={setSelectedArticle}
                  onBookmarkToggle={handleBookmarkToggle}
                />
              ))}
            </div>
          )}
        </section>

        <aside className="w-full lg:w-80">
          <TrendingSidebar articles={trending} onClick={setSelectedArticle} />
        </aside>
      </div>

      <ArticleDetailModal article={selectedArticle} isOpen={!!selectedArticle} onClose={() => setSelectedArticle(null)} />
    </div>
  );
}
