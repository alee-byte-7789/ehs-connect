import axios from "axios";
import type { AxiosError, InternalAxiosRequestConfig } from "axios";

import { tokenStorage } from "./token-storage";
import type { TokenPair } from "./types";

/**
 * Vite inlines import.meta.env.VITE_* at build time. Must be set per
 * environment (a local .env for dev, Vercel's project env vars for the
 * deployed admin portal). No safe default exists here — unlike the mobile
 * app, this always runs in a browser, so there's no "localhost fallback
 * that at least works on one machine" story; it must always be configured.
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!BASE_URL) {
  // eslint-disable-next-line no-console
  console.error(
    "[api-client] VITE_API_BASE_URL is not set. Create admin-portal/.env " +
      "with VITE_API_BASE_URL=<your backend URL>/api/v1 — see .env.example."
  );
}

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

apiClient.interceptors.request.use((config) => {
  const accessToken = tokenStorage.getAccessToken();
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
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) return null;

  try {
    const { data } = await axios.post<TokenPair>(`${BASE_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    tokenStorage.setTokens(data.access_token, data.refresh_token);
    return data;
  } catch {
    tokenStorage.clear();
    return null;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryableConfig | undefined;

    if (error.response?.status === 401 && original && !original._retried) {
      original._retried = true;

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
