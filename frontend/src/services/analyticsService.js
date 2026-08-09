import api from "./api";

export async function fetchAnalyticsSummary(days = 30) {
  const response = await api.get("/analytics/summary", {
    params: { days },
  });
  return response.data;
}
