import api from "./api";

export async function fetchAdminUsers(params = {}) {
  const { page = 1, limit = 10, search = "", role = "", sort = "newest" } = params;
  const response = await api.get("/admin/users", {
    params: { page, limit, search, role: role || undefined, sort },
  });
  return response.data;
}

export async function updateUserRole({ userId, role }) {
  const response = await api.patch(`/admin/users/${userId}/role`, { role });
  return response.data;
}
