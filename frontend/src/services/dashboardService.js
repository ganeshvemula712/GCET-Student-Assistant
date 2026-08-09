import api from "../api/axios";

const dashboardService = {
  async getStats() {
    try {
      const response = await api.get("/dashboard/stats");
      return response.data;
    } catch (error) {
      console.warn("Backend dashboard stats API warning, utilizing fallback values:", error);
      return {
        conversations: 0,
        responses: 0,
        documents: 0,
        account: "Active",
      };
    }
  },
};

export default dashboardService;