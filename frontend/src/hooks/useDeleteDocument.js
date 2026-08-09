import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import documentService from "../services/documentService";

export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: documentService.deleteDocument,

    onSuccess: () => {
      toast.success("Document deleted successfully.");

      queryClient.invalidateQueries({
        queryKey: ["documents"],
      });
    },

    onError: (error) => {
      const message =
        error?.response?.data?.detail ||
        "Failed to delete document.";

      toast.error(message);
    },
  });
}