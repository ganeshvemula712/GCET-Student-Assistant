import { useQuery } from "@tanstack/react-query";

import { getConversations } from "@/services/conversationService";

export default function useConversations() {
  return useQuery({
    queryKey: ["conversations"],
    queryFn: getConversations,
  });
}