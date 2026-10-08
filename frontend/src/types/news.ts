export type NewsCategory =
  | "technology"
  | "business"
  | "politics"
  | "health"
  | "science"
  | "world"
  | "general"
  | "sports"
  | "entertainment";

export type SentimentType = "positive" | "negative" | "neutral";
export type ImportanceType = "high" | "medium" | "low";

export interface NewsArticle {
  id: number;
  title: string;
  source: string;
  url: string;
  image_url?: string | null;
  summary: string;
  key_points: string[];
  category: NewsCategory;
  sentiment: SentimentType;
  sentiment_score?: number | null;
  importance: ImportanceType;
  published_at?: string | null;
  created_at: string;
  is_bookmarked?: boolean;
}

export interface NewsFeedParams {
  category?: NewsCategory;
  sentiment?: SentimentType;
  search?: string;
  page?: number;
  limit?: number;
}

export interface NewsFeedResponse {
  items: NewsArticle[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export interface DailyBriefing {
  date: string;
  headline_summary: string;
  top_stories: NewsArticle[];
  market_pulse?: string;
}
