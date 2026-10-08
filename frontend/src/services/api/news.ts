import { apiClient } from "./client";
import type { NewsArticle, NewsFeedResponse, DailyBriefing, NewsFeedParams } from "../../types/news";

export const newsApi = {
  getArticles: (params: NewsFeedParams = {}) => {
    const query = new URLSearchParams();
    if (params.category) query.append("category", params.category);
    if (params.sentiment) query.append("sentiment", params.sentiment);
    if (params.search) query.append("q", params.search);
    if (params.page) query.append("page", params.page.toString());
    if (params.limit) query.append("limit", params.limit.toString());

    const qs = query.toString();
    return apiClient<NewsFeedResponse>(`/news${qs ? `?${qs}` : ""}`);
  },

  getDailyBriefing: () => {
    return apiClient<DailyBriefing>("/news/briefing");
  },

  getArticle: (id: number) => {
    return apiClient<NewsArticle>(`/news/${id}`);
  },

  getBookmarks: () => {
    return apiClient<NewsArticle[]>("/bookmarks");
  },

  addBookmark: (newsId: number) => {
    return apiClient<{ message: string; bookmark_id: number }>("/bookmarks", {
      method: "POST",
      body: JSON.stringify({ news_id: newsId }),
    });
  },

  removeBookmark: (newsId: number) => {
    return apiClient<{ message: string }>(`/bookmarks/${newsId}`, {
      method: "DELETE",
    });
  },
};
