import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArticleCard } from "../components/news/ArticleCard";
import { ArticleDetailModal } from "../components/news/ArticleDetailModal";
import { Button } from "../components/ui/Button";
import { useToast } from "../context/ToastContext";
import { newsApi } from "../services/api/news";
import type { NewsArticle } from "../types/news";

export function BookmarksPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    newsApi.getBookmarks().then(setArticles).catch((requestError: { message?: string }) => {
      setError(requestError.message || "Sign in to view your saved stories.");
    });
  }, []);

  if (!localStorage.getItem("daily_news_token")) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-24 text-center sm:px-6">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-accent">Your reading list</p>
        <h1 className="mt-3 font-serif text-4xl font-bold text-foreground">Save the stories worth returning to.</h1>
        <p className="mt-4 text-foreground-muted">Sign in to keep your bookmarks available across devices.</p>
        <Button className="mt-7" onClick={() => navigate("/login")}>Sign in</Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-accent">Your reading list</p>
      <h1 className="mt-2 font-serif text-4xl font-bold text-foreground">Bookmarks</h1>
      {error ? <p className="mt-8 rounded-xl border border-red-200 bg-red-50 p-5 text-red-800">{error}</p> : null}
      {!error && articles.length === 0 ? (
        <div className="mt-10 rounded-2xl border border-dashed border-border bg-surface p-12 text-center">
          <h2 className="font-serif text-2xl font-bold text-foreground">Nothing saved yet</h2>
          <p className="mt-2 text-sm text-foreground-muted">Use the bookmark icon on any story to build your reading list.</p>
        </div>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {articles.map((article) => (
            <ArticleCard
              key={article.id}
              article={{ ...article, is_bookmarked: true }}
              onClick={setSelectedArticle}
              onBookmarkToggle={async (articleId, isBookmarked) => {
                if (isBookmarked) return true;
                try {
                  await newsApi.removeBookmark(articleId);
                  setArticles((current) => current.filter((item) => item.id !== articleId));
                  showToast("Story removed from your bookmarks.", "info");
                  return true;
                } catch (requestError) {
                  showToast((requestError as { message?: string }).message || "We couldn't remove that bookmark.", "error");
                  return false;
                }
              }}
            />
          ))}
        </div>
      )}
      <ArticleDetailModal article={selectedArticle} isOpen={!!selectedArticle} onClose={() => setSelectedArticle(null)} />
    </div>
  );
}
