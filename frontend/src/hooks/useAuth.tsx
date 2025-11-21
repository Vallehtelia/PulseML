import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { PropsWithChildren } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getMe, login as loginRequest, register as registerRequest } from "@/api/auth";
import { setAccessToken, setUnauthorizedHandler } from "@/api/client";
import type { TokenPair, UserProfile } from "@/api/types";

type AuthContextValue = {
  user: UserProfile | undefined;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<TokenPair>;
  register: (email: string, password: string) => Promise<UserProfile>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const getInitialToken = () =>
  typeof window !== "undefined" ? localStorage.getItem("pulseml_access_token") : null;

export const AuthProvider = ({ children }: PropsWithChildren) => {
  const [token, setToken] = useState<string | null>(getInitialToken);
  const queryClient = useQueryClient();

  const logout = useCallback(() => {
    setToken(null);
    setAccessToken(null);
    localStorage.removeItem("pulseml_access_token");
    localStorage.removeItem("pulseml_refresh_token");
    queryClient.clear();
  }, [queryClient]);

  useEffect(() => {
    setAccessToken(token);
  }, [token]);

  useEffect(() => {
    setUnauthorizedHandler(() => logout());
  }, [logout]);

  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: getMe,
    enabled: Boolean(token),
    staleTime: 5 * 60 * 1000,
  });

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      loginRequest(email, password),
    onSuccess: async (response) => {
      setToken(response.access_token);
      localStorage.setItem("pulseml_refresh_token", response.refresh_token);
      await queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const registerMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      registerRequest(email, password),
  });

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login: async (email: string, password: string) => {
        const result = await loginMutation.mutateAsync({ email, password });
        return result;
      },
      register: async (email: string, password: string) => {
        const result = await registerMutation.mutateAsync({ email, password });
        return result;
      },
      logout,
    }),
    [user, isLoading, loginMutation, registerMutation, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
};


