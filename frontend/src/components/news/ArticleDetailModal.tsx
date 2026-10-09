import React from "react";
import { Modal } from "../ui/Modal";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import type { NewsArticle } from "../../types/news";
import { formatDate } from "../../lib/utils";

interface ArticleDetailModalProps {
  article: NewsArticle | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ArticleDetailModal: React.FC<ArticleDetailModalProps> = ({
  article,
  isOpen,
  onClose,
}) => {
  if (!article) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} className="max-w-3xl p-0 overflow-hidden flex flex-col max-h-[90vh]">
      {/* Scrollable Content Area */}
      <div className="overflow-y-auto no-scrollbar relative flex-grow">
        {/* Hero Image */}
        {article.image_url ? (
          <div className="w-full h-64 sm:h-80 relative">
            <img src={article.image_url} alt={article.title} className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />
            <button 
              onClick={onClose}
              className="absolute top-4 right-4 bg-black/40 hover:bg-black/60 text-white rounded-full p-2 backdrop-blur-sm transition"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <div className="absolute bottom-6 left-6 right-6">
              <div className="flex gap-2 mb-3">
                <Badge variant="category" className="bg-white/10 text-white border-white/20 backdrop-blur-md">{article.category}</Badge>
                <Badge variant="sentiment" sentiment={article.sentiment} className="backdrop-blur-md bg-white/10 border-white/20">
                  {article.sentiment}
                </Badge>
              </div>
              <h2 className="text-2xl sm:text-3xl font-serif font-bold text-white leading-tight">
                {article.title}
              </h2>
            </div>
          </div>
        ) : (
          <div className="p-6 pb-0 pt-12 relative">
            <button 
              onClick={onClose}
              className="absolute top-4 right-4 text-foreground-muted hover:text-foreground rounded-full p-2 transition"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <div className="flex gap-2 mb-4">
              <Badge variant="category">{article.category}</Badge>
              <Badge variant="sentiment" sentiment={article.sentiment}>{article.sentiment}</Badge>
            </div>
            <h2 className="text-2xl sm:text-3xl font-serif font-bold text-foreground leading-tight">
              {article.title}
            </h2>
          </div>
        )}

        <div className="p-6 sm:p-8 space-y-8">
          {/* Metadata */}
          <div className="flex items-center justify-between text-sm font-medium text-foreground-muted pb-4 border-b border-border">
            <div className="flex items-center gap-2">
              <span className="text-foreground">{article.source}</span>
              <span>•</span>
              <span>{formatDate(article.published_at || article.created_at)}</span>
            </div>
          </div>

          {/* AI Summary Box */}
          <div className="bg-surface-elevated rounded-xl p-6 border border-accent/20 shadow-sm relative">
            <div className="absolute top-0 left-0 w-1.5 h-full bg-accent rounded-l-xl" />
            <div className="flex items-center gap-2 mb-4 text-accent font-bold uppercase tracking-widest text-xs">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Gemini AI Summary
            </div>
            <p className="text-base text-foreground leading-relaxed font-serif">
              {article.summary}
            </p>
          </div>

          {/* Key Takeaways */}
          {article.key_points && article.key_points.length > 0 && (
            <div>
              <h4 className="font-bold text-foreground mb-4">Key Takeaways</h4>
              <ul className="space-y-3">
                {article.key_points.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-sm text-foreground-muted">
                    <span className="flex-shrink-0 w-1.5 h-1.5 mt-1.5 rounded-full bg-accent" />
                    <span className="leading-relaxed">{point}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Footer Actions */}
      <div className="p-4 sm:p-6 bg-surface border-t border-border flex items-center justify-end gap-3 flex-shrink-0">
        <Button variant="ghost" onClick={onClose}>
          Close
        </Button>
        <Button 
          variant="primary" 
          onClick={() => window.open(article.url, "_blank", "noopener,noreferrer")}
          className="gap-2"
        >
          Read Original Article
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </Button>
      </div>
    </Modal>
  );
};
