import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import documentService from "@/services/documentService";
import { formatErrorMessage } from "@/utils/error";

export function useReindexDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId) => documentService.reindexDocument(documentId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success(data?.message || "Document re-indexed successfully into ChromaDB!");
    },
    onError: (error) => {
      const errorMsg = formatErrorMessage(error, "Failed to re-index document.");
      toast.error(errorMsg);
    },
  });
}
