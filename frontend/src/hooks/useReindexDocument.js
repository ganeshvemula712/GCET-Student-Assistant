import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import documentService from "@/services/documentService";

export function useReindexDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId) => documentService.reindexDocument(documentId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success(data?.message || "Document re-indexed successfully into ChromaDB!");
    },
    onError: (error) => {
      const errorMsg =
        error?.response?.data?.detail || "Failed to re-index document.";
      toast.error(errorMsg);
    },
  });
}
