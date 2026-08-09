import { useMutation, useQueryClient } from "@tanstack/react-query";
import { renameConversation } from "@/services/conversationService";

export default function useRenameConversation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, title }) =>
      renameConversation(id, title),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["conversations"],
      });
    },
  });
}