import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  regenerateMessage,
} from "@/services/messageService";

export default function useRegenerateMessage() {

  const queryClient = useQueryClient();

  return useMutation({

    mutationFn: ({
      messageId,
    }) =>
      regenerateMessage(
        messageId
      ),

    onSuccess: (
      _,
      variables,
    ) => {

      if (
        variables?.conversationId
      ) {

        queryClient.invalidateQueries({
          queryKey: [
            "conversation",
            variables.conversationId,
          ],
        });

      }

      queryClient.invalidateQueries({
        queryKey: [
          "conversations",
        ],
      });

    },

  });

}