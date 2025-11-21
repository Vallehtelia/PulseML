import { apiClient } from "./client";
import type { TokenPair, UserProfile } from "./types";

export const login = async (email: string, password: string): Promise<TokenPair> => {
  const { data } = await apiClient.post<TokenPair>("/auth/login", { email, password });
  return data;
};

export const register = async (email: string, password: string): Promise<UserProfile> => {
  const { data } = await apiClient.post<UserProfile>("/auth/register", {
    email,
    password,
  });
  return data;
};

export const getMe = async (): Promise<UserProfile> => {
  const { data } = await apiClient.get<UserProfile>("/auth/me");
  return data;
};


