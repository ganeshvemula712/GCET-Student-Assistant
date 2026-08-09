import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateMessage } from "@/services/messageService";

export default function useUpdateMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ messageId, content }) =>
      updateMessage(messageId, content),

    onSuccess: () => {
      queryClient.invalidateQueries();
    },
  });
}