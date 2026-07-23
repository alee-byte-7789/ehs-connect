import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

import { tokenStorage } from "./token-storage";
import type { TokenPair } from "./types";

/**
 * Must be set per environment via `EXPO_PUBLIC_API_BASE_URL` (e.g. in a
 * `.env` file, gitignored). There is no safe default that works from a
 * physical phone — "localhost" only resolves on the same machine the
 * backend runs on, so every developer points this at their own machine's
 * LAN IP (e.g. http://192.168.1.20:8000/api/v1) while testing with Expo Go
 * or the web/PWA build on a real device.
 */
const BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

if (!process.env.EXPO_PUBLIC_API_BASE_URL) {
  // eslint-disable-next-line no-console
  console.warn(
    "[api-client] EXPO_PUBLIC_API_BASE_URL is not set — falling back to " +
      "http://localhost:8000/api/v1, which will NOT work from a physical " +
      "device or the iOS PWA. Set it in mobile-app/.env."
  );
}

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

apiClient.interceptors.request.use(async (config) => {
  const accessToken = await tokenStorage.getAccessToken();
  if (accessToken) {
    config.headers.set("Authorization", `Bearer ${accessToken}`);
  }
  return config;
});

interface RetryableConfig extends InternalAxiosRequestConfig {
  _retried?: boolean;
}

let refreshInFlight: Promise<TokenPair | null> | null = null;

async function refreshTokens(): Promise<TokenPair | null> {
  const refreshToken = await tokenStorage.getRefreshToken();
  if (!refreshToken) return null;

  try {
    // Use a bare axios call (not `apiClient`) to avoid recursing through
    // these same interceptors.
    const { data } = await axios.post<TokenPair>(`${BASE_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    await tokenStorage.setTokens(data.access_token, data.refresh_token);
    return data;
  } catch {
    await tokenStorage.clear();
    return null;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryableConfig | undefined;

    if (error.response?.status === 401 && original && !original._retried) {
      original._retried = true;

      // Coalesce concurrent 401s into a single refresh call.
      refreshInFlight ??= refreshTokens().finally(() => {
        refreshInFlight = null;
      });
      const refreshed = await refreshInFlight;

      if (refreshed) {
        original.headers.set("Authorization", `Bearer ${refreshed.access_token}`);
        return apiClient.request(original);
      }
    }

    return Promise.reject(error);
  }
);

/** Pulls a readable message out of FastAPI's error shape (`detail` as string, or Pydantic's list-of-errors). */
export function extractApiErrorMessage(error: unknown, fallback = "Something went wrong. Please try again."): string {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((d) => (typeof d === "string" ? d : d?.msg)).filter(Boolean).join(" ");
    }
  }
  return fallback;
}
