import { useMutation, useQueryClient } from "@tanstack/react-query";

import { deleteMessage } from "@/services/messageService";

export default function useDeleteMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ messageId }) =>
      deleteMessage(messageId),

    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: [
          "conversation",
          variables.conversationId,
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "conversations",
        ],
      });
    },
  });
}