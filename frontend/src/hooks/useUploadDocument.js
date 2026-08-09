import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import documentService from "../services/documentService";

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, supersedesId }) => documentService.uploadDocument(file, supersedesId),

    onSuccess: (data) => {
      toast.success(data?.message || "Document uploaded and indexed successfully.");

      queryClient.invalidateQueries({
        queryKey: ["documents"],
      });
      queryClient.invalidateQueries({
        queryKey: ["dashboard-stats"],
      });
      queryClient.invalidateQueries({
        queryKey: ["analytics-summary"],
      });
    },

    onError: (error) => {
      const message =
        error?.response?.data?.detail ||
        "Failed to upload document.";

      toast.error(message);
    },
  });
}