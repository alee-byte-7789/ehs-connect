import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { apiClient } from "./api-client";
import { tokenStorage } from "./token-storage";
import type { LoginRequest, RegisterRequest, RegisterResponse, TokenPair } from "./types";

type AuthStatus = "checking" | "signed-out" | "signed-in";

interface AuthContextValue {
  status: AuthStatus;
  login: (payload: LoginRequest) => Promise<void>;
  register: (payload: RegisterRequest) => Promise<RegisterResponse>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("checking");

  useEffect(() => {
    tokenStorage.getAccessToken().then((token) => {
      setStatus(token ? "signed-in" : "signed-out");
    });
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      status,

      async login(payload: LoginRequest) {
        const { data } = await apiClient.post<TokenPair>("/auth/login", payload);
        await tokenStorage.setTokens(data.access_token, data.refresh_token);
        setStatus("signed-in");
      },

      async register(payload: RegisterRequest) {
        const { data } = await apiClient.post<RegisterResponse>("/auth/register", payload);
        // Registration never signs the resident in — verification_status is
        // "pending" until a Housing Office Admin approves it (see roadmap
        // Section 6.3). The caller routes to the Pending screen next.
        return data;
      },

      async logout() {
        const refreshToken = await tokenStorage.getRefreshToken();
        if (refreshToken) {
          // Best-effort: revoke server-side, but never block local logout on it.
          apiClient.post("/auth/logout", { refresh_token: refreshToken }).catch(() => undefined);
        }
        await tokenStorage.clear();
        setStatus("signed-out");
      },
    }),
    [status]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
