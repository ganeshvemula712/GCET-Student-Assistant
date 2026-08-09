import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { toast } from "sonner";

export default function LogoutButton() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  function handleLogout() {
    logout();
    toast.success("Logged out successfully.");
    navigate("/");
  }

  return (
    <button
      onClick={handleLogout}
      className="rounded-xl bg-red-600 px-5 py-3 font-semibold transition hover:bg-red-700"
    >
      Logout
    </button>
  );
}