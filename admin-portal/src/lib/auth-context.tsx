import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

import { apiClient } from "./api-client";
import { tokenStorage } from "./token-storage";
import type { AdminLoginRequest, TokenPair } from "./types";

type AuthStatus = "signed-out" | "signed-in";

interface AuthContextValue {
  status: AuthStatus;
  login: (payload: AdminLoginRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>(
    tokenStorage.getAccessToken() ? "signed-in" : "signed-out"
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      status,

      async login(payload: AdminLoginRequest) {
        const { data } = await apiClient.post<TokenPair>("/auth/admin/login", payload);
        tokenStorage.setTokens(data.access_token, data.refresh_token);
        setStatus("signed-in");
      },

      logout() {
        const refreshToken = tokenStorage.getRefreshToken();
        if (refreshToken) {
          apiClient.post("/auth/logout", { refresh_token: refreshToken }).catch(() => undefined);
        }
        tokenStorage.clear();
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
