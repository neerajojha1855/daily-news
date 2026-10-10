import type { NewsCategory } from "./news";

export interface UserPreferences {
  preferred_categories: NewsCategory[];
  preferred_sources: string[];
  preferred_language: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
  last_login_at?: string | null;
}

export interface UserProfile extends User {
  stats: {
    total_bookmarks: number;
  };
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
