"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { apiClient, setAccessToken, onSessionExpired } from "./api-client";
import { TokenResponse, UserSummary, UserMeResponse } from "@/types";

interface AuthContextValue {
  user: UserSummary | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<TokenResponse>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<UserSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Re-fetch current user session on demand
  const refreshUser = useCallback(async () => {
    try {
      const data = await apiClient<UserMeResponse>("/users/me");
      setUser({
        id: data.id,
        email: data.email,
        role: data.role,
        status: data.status,
      });
    } catch {
      setUser(null);
      setAccessToken(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initialize session on mount via /users/me
  useEffect(() => {
    let isMounted = true;

    async function initializeSession() {
      try {
        const data = await apiClient<UserMeResponse>("/users/me");
        if (isMounted) {
          setUser({
            id: data.id,
            email: data.email,
            role: data.role,
            status: data.status,
          });
        }
      } catch {
        if (isMounted) {
          setUser(null);
          setAccessToken(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void initializeSession();

    // Register session expired handler to cleanly clear state and redirect
    onSessionExpired(() => {
      setUser(null);
      setAccessToken(null);
      if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
        router.push(`/login?redirect=${encodeURIComponent(window.location.pathname)}`);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [router]);

  const login = async (email: string, password: string): Promise<TokenResponse> => {
    const data = await apiClient<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
        client_type: "WEB",
      }),
    });
    setAccessToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const logout = async (): Promise<void> => {
    try {
      await apiClient("/auth/logout", { method: "POST" });
    } catch {
      // Ignore network errors during logout
    } finally {
      setAccessToken(null);
      setUser(null);
      router.push("/login");
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
