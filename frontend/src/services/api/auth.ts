import { apiClient } from "./client";
import type { AuthResponse, User, UserPreferences } from "../../types/user";

export const authApi = {
  login: (email: string, password: string) => {
    return apiClient<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  register: (username: string, email: string, password: string, confirmPassword: string) => {
    return apiClient<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        username,
        email,
        password,
        confirm_password: confirmPassword,
      }),
    });
  },

  getMe: () => {
    return apiClient<User>("/auth/me");
  },

  updatePreferences: (preferences: UserPreferences) => {
    return apiClient<UserPreferences>("/preferences", {
      method: "PUT",
      body: JSON.stringify(preferences),
    });
  },
};
