"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User, ApiError } from "@/types";
import { getToken, setToken, clearToken } from "@/lib/auth";
import { apiFetch } from "@/lib/api";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = getToken();
    if (storedToken) {
      setTokenState(storedToken);
      apiFetch<User>("/users/me")
        .then((u) => setUser(u))
        .catch((err: ApiError) => {
          if (err.status === 401) {
            clearToken();
            setTokenState(null);
          }
        })
        .finally(() => setIsLoading(false));
      return;
    }

    // In preview environments, auto-login as test user
    if (process.env.NEXT_PUBLIC_PREVIEW_MODE === "true") {
      apiFetch<{ token: string }>("/auth/test-login")
        .then(({ token: t }) => login(t))
        .catch(() => {})
        .finally(() => setIsLoading(false));
      return;
    }

    setIsLoading(false);
  }, []);

  const login = async (newToken: string) => {
    setToken(newToken);
    setTokenState(newToken);
    const u = await apiFetch<User>("/users/me");
    setUser(u);
  };

  const logout = () => {
    clearToken();
    setTokenState(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
