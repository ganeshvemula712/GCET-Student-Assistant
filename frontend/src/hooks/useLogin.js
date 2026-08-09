import { useMutation } from "@tanstack/react-query";
import { login } from "@/services/authService";

export default function useLogin() {
  return useMutation({
    mutationFn: ({ email, password }) =>
      login(email, password),
  });
}