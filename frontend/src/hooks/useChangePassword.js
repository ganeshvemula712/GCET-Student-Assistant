import { useMutation } from "@tanstack/react-query";
import { changePassword } from "@/services/userService";

export default function useChangePassword() {
  return useMutation({
    mutationFn: changePassword,
  });
}