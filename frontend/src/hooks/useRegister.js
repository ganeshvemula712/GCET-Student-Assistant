import { useMutation } from "@tanstack/react-query";

import { register } from "@/services/authService";

export default function useRegister() {
  return useMutation({ mutationFn: register });
}
