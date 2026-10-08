import { apiClient } from "./client";
import type { AuthResponse, User, UserPreferences } from "../../types/user";

export const authApi = {
  login: (email: string, password: string) => {
    return apiClient<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  register: (email: string, password: string, fullName?: string) => {
    return apiClient<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
  },

  getMe: () => {
    return apiClient<User>("/profile/me");
  },

  updatePreferences: (preferences: Partial<UserPreferences>) => {
    return apiClient<User>("/preferences", {
      method: "PUT",
      body: JSON.stringify(preferences),
    });
  },
};
