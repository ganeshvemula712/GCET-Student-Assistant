import { useQuery } from "@tanstack/react-query";
import api from "@/services/api";

async function searchConversations(query) {
  if (!query.trim()) return [];

  const { data } = await api.get(
    `/conversations/search?q=${encodeURIComponent(query)}`
  );

  return data;
}

export default function useSearchConversation(query) {
  return useQuery({
    queryKey: ["conversation-search", query],
    queryFn: () => searchConversations(query),
    enabled: query.trim().length > 0,
  });
}