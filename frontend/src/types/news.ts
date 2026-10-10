export type NewsCategory =
  | "technology"
  | "business"
  | "politics"
  | "health"
  | "science"
  | "world"
  | "sports"
  | "entertainment"
  | "india"
  | "education"
  | "environment"
  | "other";

export type SentimentType = "positive" | "negative" | "neutral" | "mixed";
export type ImportanceType = "high" | "medium" | "low";

export interface NewsArticle {
  id: string;
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
  published_at: string;
  created_at: string;
  is_bookmarked?: boolean;
}

export interface NewsFeedParams {
  category?: NewsCategory;
  sort?: "latest" | "importance" | "trending" | "recommended";
  page?: number;
  pageSize?: number;
}

export interface NewsFeedResponse {
  items: NewsArticle[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DailyBriefing {
  date: string;
  headline_summary: string;
  top_stories: NewsArticle[];
  market_pulse?: string;
}
