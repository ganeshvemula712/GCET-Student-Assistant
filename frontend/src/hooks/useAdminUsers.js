import { useQuery } from "@tanstack/react-query";
import { fetchAdminUsers } from "@/services/adminService";

export default function useAdminUsers(params = {}) {
  return useQuery({
    queryKey: ["admin", "users", params],
    queryFn: () => fetchAdminUsers(params),
    staleTime: 1000 * 30,
  });
}
