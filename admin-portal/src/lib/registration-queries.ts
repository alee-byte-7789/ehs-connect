import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "./api-client";
import type { AdminOut, RegistrationApprovedOut, RegistrationRejectedOut, ResidentOut } from "./types";

export function useAdminMe(enabled: boolean) {
  return useQuery<AdminOut>({
    queryKey: ["admins", "me"],
    queryFn: async () => (await apiClient.get<AdminOut>("/admins/me")).data,
    enabled,
  });
}

export function usePendingRegistrations() {
  return useQuery<ResidentOut[]>({
    queryKey: ["registrations", "pending"],
    queryFn: async () => (await apiClient.get<ResidentOut[]>("/registrations/pending")).data,
  });
}

export function useApproveRegistration() {
  const queryClient = useQueryClient();
  return useMutation<RegistrationApprovedOut, unknown, number>({
    mutationFn: async (residentId: number) =>
      (await apiClient.post<RegistrationApprovedOut>(`/registrations/${residentId}/approve`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["registrations", "pending"] });
    },
  });
}

export function useRejectRegistration() {
  const queryClient = useQueryClient();
  return useMutation<RegistrationRejectedOut, unknown, number>({
    mutationFn: async (residentId: number) =>
      (await apiClient.post<RegistrationRejectedOut>(`/registrations/${residentId}/reject`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["registrations", "pending"] });
    },
  });
}
