const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export interface ApiError {
  status: number;
  message: string;
  details?: unknown;
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("daily_news_token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = `${BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = "An unexpected error occurred.";
    try {
      const errorJson = await response.json();
      errorDetail =
        errorJson.error?.message ||
        errorJson.detail ||
        errorJson.message ||
        errorDetail;
    } catch {
      // Some error responses do not contain JSON.
    }

    const err: ApiError = {
      status: response.status,
      message: errorDetail,
    };
    throw err;
  }

  if (response.status === 204) {
    return {} as T;
  }

  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    throw {
      status: response.status,
      message:
        "The API returned a non-JSON response. Start the FastAPI server on port 8000 or set VITE_API_BASE_URL to the deployed API URL.",
    } satisfies ApiError;
  }

  return response.json() as Promise<T>;
}
