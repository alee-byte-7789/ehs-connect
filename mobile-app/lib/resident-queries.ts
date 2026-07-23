import { useQuery } from "@tanstack/react-query";

import { apiClient } from "./api-client";
import type { ResidentOut } from "./types";

export function useResidentMe(enabled: boolean) {
  return useQuery<ResidentOut>({
    queryKey: ["residents", "me"],
    queryFn: async () => {
      const { data } = await apiClient.get<ResidentOut>("/residents/me");
      return data;
    },
    enabled,
  });
}
