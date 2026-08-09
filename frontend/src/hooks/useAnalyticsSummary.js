import { useQuery } from "@tanstack/react-query";
import { fetchAnalyticsSummary } from "@/services/analyticsService";

export default function useAnalyticsSummary(days = 30) {
  return useQuery({
    queryKey: ["analytics", "summary", days],
    queryFn: () => fetchAnalyticsSummary(days),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}
