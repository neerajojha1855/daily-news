import { apiClient } from "./client";
import type { User, UserPreferences, UserProfile } from "../../types/user";

export const profileApi = {
  getProfile: () => apiClient<UserProfile>("/profile"),

  updateProfile: (profile: Pick<User, "username" | "email">) =>
    apiClient<User>("/profile", {
      method: "PUT",
      body: JSON.stringify(profile),
    }),

  getPreferences: () => apiClient<UserPreferences>("/preferences"),

  updatePreferences: (preferences: UserPreferences) =>
    apiClient<UserPreferences>("/preferences", {
      method: "PUT",
      body: JSON.stringify(preferences),
    }),

  changePassword: (currentPassword: string, newPassword: string) =>
    apiClient<{ message: string }>("/profile/password", {
      method: "PUT",
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    }),
};
