/**
 * Theme-related hooks using TanStack Query.
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { logger } from "@/lib/logger";
import { useAuthStore } from "@/store/authStore";
import { authKeys } from "@/hooks/useAuth";
import type { ThemePreference } from "@/types/theme";
import type { User } from "@/types/user";

/**
 * Hook to update the user's theme preference.
 */
export function useUpdateThemePreference() {
  const setUser = useAuthStore((state) => state.setUser);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (theme: ThemePreference): Promise<User> => {
      const response = await api.patch("/api/v1/auth/me/theme", {
        theme_preference: theme,
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Update auth store with new user data
      setUser(data);
      // Update query cache
      queryClient.setQueryData(authKeys.user(), data);
      logger.info("Theme preference saved to server", { theme: data.theme_preference });
    },
    onError: (error) => {
      logger.error("Failed to save theme preference", { error });
    },
  });
}
