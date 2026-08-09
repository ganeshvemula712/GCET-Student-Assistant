import { useQuery } from "@tanstack/react-query";

import { getConversation } from "@/services/conversationService";

export default function useConversation(conversationId) {
  return useQuery({
    queryKey: ["conversation", conversationId],

    queryFn: () =>
      getConversation(conversationId),

    enabled: !!conversationId,

    staleTime: 0,

    refetchOnMount: true,

    refetchOnWindowFocus: false,

    refetchOnReconnect: true,
  });
}