import React, { useState } from "react";
import type { NewsArticle } from "../../types/news";
import { Badge } from "../ui/Badge";
import { formatDate, truncateText } from "../../lib/utils";

interface ArticleCardProps {
  article: NewsArticle;
  onBookmarkToggle?: (id: string, isBookmarked: boolean) => void | Promise<boolean>;
  onClick?: (article: NewsArticle) => void;
  featured?: boolean;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({
  article,
  onBookmarkToggle,
  onClick,
  featured = false,
}) => {
  const [imgError, setImgError] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(article.is_bookmarked || false);

  const handleBookmark = async (e: React.MouseEvent) => {
    e.stopPropagation();
    const newState = !isBookmarked;
    if (onBookmarkToggle) {
      const result = await onBookmarkToggle(article.id, newState);
      if (result === false) return;
    }
    setIsBookmarked(newState);
  };

  return (
    <article
      onClick={() => onClick && onClick(article)}
      className="group flex flex-col bg-surface border border-border rounded-xl overflow-hidden hover:shadow-lg transition-all cursor-pointer h-full"
    >
      {/* Image Container */}
      <div className={`relative w-full overflow-hidden bg-slate-100 dark:bg-slate-800 ${featured ? 'h-64' : 'h-48'}`}>
        {!imgError && article.image_url ? (
          <img
            src={article.image_url}
            alt={article.title}
            onError={() => setImgError(true)}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-foreground-muted">
            <svg className="w-12 h-12 opacity-20" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5-7l-3 3.72L9 13l-3 4h14l-4-5z" />
            </svg>
          </div>
        )}
        <div className="absolute top-3 left-3 flex gap-2">
          <Badge variant="category">{article.category}</Badge>
          {article.importance === "high" && <Badge variant="importance" importance="high">Hot</Badge>}
        </div>
        <button
          onClick={handleBookmark}
          className="absolute top-3 right-3 p-2 rounded-full bg-black/30 hover:bg-black/50 backdrop-blur-md text-white transition-colors"
          aria-label={isBookmarked ? "Remove bookmark" : "Add bookmark"}
        >
          <svg className={`w-5 h-5 ${isBookmarked ? 'fill-current text-red-500' : 'stroke-current fill-none'}`} viewBox="0 0 24 24" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 4.5A2.5 2.5 0 018.5 2h7A2.5 2.5 0 0118 4.5v17l-6-3.75L6 21.5v-17z" />
          </svg>
        </button>
      </div>

      {/* Content Container */}
      <div className="p-5 flex flex-col flex-grow">
        <div className="flex items-center gap-2 mb-2 text-xs font-medium text-foreground-muted">
          <span>{article.source}</span>
          <span>•</span>
          <span>{formatDate(article.published_at || article.created_at)}</span>
        </div>
        
        <h3 className={`font-serif font-bold text-foreground mb-3 leading-tight group-hover:text-accent transition-colors ${featured ? 'text-2xl' : 'text-lg'}`}>
          {article.title}
        </h3>
        
        <p className="text-sm text-foreground-muted mb-4 line-clamp-3">
          {truncateText(article.summary, 180)}
        </p>

        <div className="mt-auto pt-4 border-t border-border flex items-center justify-between">
          <Badge variant="sentiment" sentiment={article.sentiment}>
            {article.sentiment} {article.sentiment_score ? `(${(article.sentiment_score * 100).toFixed(0)}%)` : ''}
          </Badge>
          <span className="text-xs font-medium text-accent flex items-center gap-1 group-hover:underline">
            Read Insights
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </span>
        </div>
      </div>
    </article>
  );
};