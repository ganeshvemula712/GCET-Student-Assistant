import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteConversation } from "@/services/conversationService";

export default function useDeleteConversation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteConversation,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["conversations"],
      });
    },
  });
}