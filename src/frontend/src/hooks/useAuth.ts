/**
 * Authentication hooks using TanStack Query.
 * All server state management for auth goes through these hooks.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

import { api } from "@/lib/api";
import { logger } from "@/lib/logger";
import { useAuthStore } from "@/store/authStore";
import { useThemeStore } from "@/store/themeStore";
import type { LoginCredentials, RegisterData, User, UserUpdate, PasswordChange } from "@/types/user";

// Query keys
export const authKeys = {
  all: ["auth"] as const,
  user: () => [...authKeys.all, "user"] as const,
};

/**
 * Hook to get the current user.
 */
export function useCurrentUser() {
  const setUser = useAuthStore((state) => state.setUser);
  const setLoading = useAuthStore((state) => state.setLoading);
  const setTheme = useThemeStore((state) => state.setTheme);

  const query = useQuery({
    queryKey: authKeys.user(),
    queryFn: async (): Promise<User> => {
      const response = await api.get("/api/v1/auth/me");
      return response.data;
    },
    retry: false,
  });

  // Handle success/error with useEffect
  useEffect(() => {
    if (query.isSuccess) {
      setUser(query.data);
      // Sync theme preference from user data on initial load
      // Server theme takes precedence over localStorage for authenticated users
      if (query.data.theme_preference) {
        setTheme(query.data.theme_preference);
      }
      setLoading(false);
    }
    if (query.isError) {
      setUser(null);
      setLoading(false);
    }
  }, [query.isSuccess, query.isError, query.data, setUser, setLoading, setTheme]);

  return query;
}

/**
 * Hook to login.
 */
export function useLogin() {
  const setUser = useAuthStore((state) => state.setUser);
  const setTheme = useThemeStore((state) => state.setTheme);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (credentials: LoginCredentials): Promise<User> => {
      // First login to set the cookie
      await api.post("/api/v1/auth/login", credentials, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      
      // Then get the user
      const response = await api.get("/api/v1/auth/me");
      return response.data;
    },
    onSuccess: (data) => {
      setUser(data);
      // Sync theme preference from user data
      // Server theme takes precedence over localStorage for authenticated users
      if (data.theme_preference) {
        setTheme(data.theme_preference);
      }
      queryClient.setQueryData(authKeys.user(), data);
      logger.info("User logged in successfully", { username: data.username });
    },
    onError: (error) => {
      logger.error("Login failed", { error });
    },
  });
}

/**
 * Hook to register.
 */
export function useRegister() {
  return useMutation({
    mutationFn: async (data: RegisterData): Promise<User> => {
      const response = await api.post("/api/v1/auth/register", data);
      return response.data;
    },
    onSuccess: (data) => {
      logger.info("User registered successfully", { username: data.username });
    },
    onError: (error) => {
      logger.error("Registration failed", { error });
    },
  });
}

/**
 * Hook to logout.
 */
export function useLogout() {
  const logout = useAuthStore((state) => state.logout);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (): Promise<void> => {
      await api.post("/api/v1/auth/logout");
    },
    onSuccess: () => {
      logout();
      queryClient.clear();
      logger.info("User logged out successfully");
    },
    onError: (error) => {
      logger.error("Logout failed", { error });
      // Still logout locally even if server request fails
      logout();
      queryClient.clear();
    },
  });
}

/**
 * Hook to update profile.
 */
export function useUpdateProfile() {
  const setUser = useAuthStore((state) => state.setUser);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: UserUpdate): Promise<User> => {
      const response = await api.put("/api/v1/auth/me", data);
      return response.data;
    },
    onSuccess: (data) => {
      setUser(data);
      queryClient.setQueryData(authKeys.user(), data);
      logger.info("Profile updated successfully");
    },
    onError: (error) => {
      logger.error("Profile update failed", { error });
    },
  });
}

/**
 * Hook to change password.
 */
export function useChangePassword() {
  return useMutation({
    mutationFn: async (data: PasswordChange): Promise<void> => {
      await api.put("/api/v1/auth/me/password", data);
    },
    onSuccess: () => {
      logger.info("Password changed successfully");
    },
    onError: (error) => {
      logger.error("Password change failed", { error });
    },
  });
}
