import type { NewsCategory } from "./news";

export interface UserPreferences {
  categories: NewsCategory[];
  daily_digest_enabled: boolean;
  theme?: "light" | "dark" | "system";
}

export interface User {
  id: number;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  preferences: UserPreferences;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface AuthResponse {
  user: User;
  token: AuthTokens;
}
