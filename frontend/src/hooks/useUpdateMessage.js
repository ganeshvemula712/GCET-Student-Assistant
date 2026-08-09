import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateMessage } from "@/services/messageService";

export default function useUpdateMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ messageId, content }) =>
      updateMessage(messageId, content),

    onSuccess: (_, variables) => {
      if (variables?.conversationId) {
        queryClient.invalidateQueries({
          queryKey: ["conversation", variables.conversationId],
        });
      }

      queryClient.invalidateQueries({
        queryKey: ["conversations"],
      });
    },
  });
}