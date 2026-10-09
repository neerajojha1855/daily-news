import React from "react";
import type { NewsArticle } from "../../types/news";

interface TrendingSidebarProps {
  articles: NewsArticle[];
  onClick: (article: NewsArticle) => void;
}

export const TrendingSidebar: React.FC<TrendingSidebarProps> = ({ articles, onClick }) => {
  if (!articles || articles.length === 0) return null;

  return (
    <div className="bg-surface rounded-2xl p-6 border border-border shadow-sm sticky top-6">
      <h3 className="text-lg font-bold font-serif text-foreground mb-6 flex items-center gap-2">
        <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
        Trending Now
      </h3>
      
      <div className="flex flex-col gap-6">
        {articles.slice(0, 5).map((article, index) => (
          <article 
            key={article.id} 
            className="flex gap-4 cursor-pointer group"
            onClick={() => onClick(article)}
          >
            <span className="text-3xl font-serif font-bold text-border group-hover:text-accent transition-colors">
              {index + 1}
            </span>
            <div className="flex flex-col">
              <h4 className="font-medium text-foreground text-sm leading-snug mb-1 group-hover:underline">
                {article.title}
              </h4>
              <span className="text-xs text-foreground-muted">{article.source}</span>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
};
