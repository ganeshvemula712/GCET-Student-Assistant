import { useQuery } from "@tanstack/react-query";
import documentService from "../services/documentService";

export function useDocuments(options = {}) {
  return useQuery({
    queryKey: ["documents"],
    queryFn: documentService.getDocuments,
    staleTime: 1000 * 60 * 5, // 5 minutes
    enabled: options.enabled ?? true,
    retry: (failureCount, error) => {
      if (error?.response?.status === 403) return false;
      return failureCount < 2;
    },
  });
}