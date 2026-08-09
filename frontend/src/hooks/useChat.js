import { useMutation, useQueryClient } from "@tanstack/react-query";

import { askAI } from "@/services/chatService";

export default function useChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ conversationId, question, token, onChunk, onComplete, onAbort, signal }) =>
      askAI({
        conversationId,
        question,
        token,
        onChunk,
        onComplete,
        onAbort,
        signal,
      }),

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