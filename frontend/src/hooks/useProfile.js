import { useQuery } from "@tanstack/react-query";
import { getProfile } from "@/services/userService";

export default function useProfile() {
  return useQuery({
    queryKey: ["profile"],
    queryFn: getProfile,
  });
}