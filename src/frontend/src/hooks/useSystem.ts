/**
 * System/Health hooks for backend status and version
 */

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

interface HealthResponse {
  status: string;
  version: string;
}

/**
 * Hook to fetch backend health and version info
 */
export function useBackendHealth() {
  return useQuery<HealthResponse>({
    queryKey: ["health"],
    queryFn: async () => {
      const response = await api.get("/health");
      return response.data;
    },
    retry: 1,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}
