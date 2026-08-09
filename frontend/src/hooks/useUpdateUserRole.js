import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateUserRole } from "@/services/adminService";

export default function useUpdateUserRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, role }) => updateUserRole({ userId, role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}
