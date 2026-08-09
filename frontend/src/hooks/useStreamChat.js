import { useMutation, useQueryClient } from "@tanstack/react-query";

import { askAI } from "@/services/chatService";

export default function useStreamChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: askAI,

    onSuccess: (_, variables) => {
      const conversationId = variables?.conversationId ?? variables?.conversation_id;

      if (conversationId) {
        queryClient.invalidateQueries({
          queryKey: ["conversation", conversationId],
        });
      }

      queryClient.invalidateQueries({
        queryKey: ["conversations"],
      });
    },
  });
}