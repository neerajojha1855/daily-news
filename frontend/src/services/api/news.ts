import { apiClient } from "./client";
import type { NewsArticle, NewsFeedResponse, NewsCategory, NewsFeedParams } from "../../types/news";

interface ApiArticle {
  id: string;
  title: string;
  description?: string | null;
  url: string;
  image_url?: string | null;
  source_name: string;
  published_at: string;
  category: NewsCategory;
  summary?: string | null;
  topics?: string[];
  sentiment: NewsArticle["sentiment"];
  importance_score: number;
}

interface ApiArticleSearchResult {
  articles: ApiArticle[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface ApiBookmark {
  article: ApiArticle;
}

const normalizeArticle = (article: ApiArticle): NewsArticle => ({
  id: article.id,
  title: article.title,
  source: article.source_name,
  url: article.url,
  image_url: article.image_url,
  summary: article.summary || article.description || "No summary is available for this story yet.",
  key_points: article.topics || [],
  category: article.category,
  sentiment: article.sentiment,
  sentiment_score: null,
  importance: article.importance_score >= 0.75 ? "high" : article.importance_score >= 0.4 ? "medium" : "low",
  published_at: article.published_at,
  created_at: article.published_at,
});

export const newsApi = {
  async getArticles(params: NewsFeedParams = {}): Promise<NewsFeedResponse> {
    const query = new URLSearchParams();
    if (params.category) query.append("category", params.category);
    if (params.sort) query.append("sort", params.sort);
    if (params.page) query.append("page", params.page.toString());
    if (params.pageSize) query.append("page_size", params.pageSize.toString());

    const qs = query.toString();
    const response = await apiClient<ApiArticleSearchResult>(`/news${qs ? `?${qs}` : ""}`);
    return {
      items: response.articles.map(normalizeArticle),
      total: response.total,
      page: response.page,
      page_size: response.page_size,
      total_pages: response.total_pages,
    };
  },

  async getTrending(limit = 5): Promise<NewsArticle[]> {
    const response = await apiClient<ApiArticle[]>(`/news/trending?limit=${limit}`);
    return response.map(normalizeArticle);
  },

  async getArticle(id: string): Promise<NewsArticle> {
    const response = await apiClient<ApiArticle>(`/news/${id}`);
    return normalizeArticle(response);
  },

  async getBookmarks(): Promise<NewsArticle[]> {
    const response = await apiClient<ApiBookmark[]>("/bookmarks");
    return response.map((bookmark) => normalizeArticle(bookmark.article));
  },

  addBookmark: (articleId: string) => {
    return apiClient<{ message: string; article_id: string }>(`/bookmarks/${articleId}`, {
      method: "POST",
    });
  },

  removeBookmark: (articleId: string) => {
    return apiClient<{ message: string }>(`/bookmarks/${articleId}`, {
      method: "DELETE",
    });
  },
};
