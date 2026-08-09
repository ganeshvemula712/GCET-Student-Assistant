import { NavLink } from "react-router-dom";
import { toast } from "sonner";
import {
  House,
  ChatCircleDots,
  Files,
  User,
  Gear,
  ChartBar,
  ShieldCheck,
  SignOut,
} from "@phosphor-icons/react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import useProfile from "@/hooks/useProfile";
import GcetLogo from "@/components/common/GcetLogo";

const menu = [
  {
    title: "Dashboard",
    icon: House,
    path: "/dashboard",
  },
  {
    title: "AI Assistant",
    icon: ChatCircleDots,
    path: "/chat",
  },
  {
    title: "Analytics",
    icon: ChartBar,
    path: "/analytics",
  },
  {
    title: "Documents",
    icon: Files,
    path: "/documents",
  },
  {
    title: "Profile",
    icon: User,
    path: "/profile",
  },
  {
    title: "Settings",
    icon: Gear,
    path: "/settings",
  },
  {
    title: "Admin Panel",
    icon: ShieldCheck,
    path: "/admin",
  },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { data: profile } = useProfile();

  function handleLogout() {
    logout();
    toast.success("Logged out successfully.");
    navigate("/");
  }

  const isAdmin = profile?.role === "admin";

  const displayMenu = menu.filter((item) => item.path !== "/admin" || isAdmin);

  return (
    <aside className="fixed left-0 top-0 hidden h-screen w-56 border-r border-white/10 bg-[#0B1120] lg:flex lg:flex-col">
      <div className="flex items-center gap-3 border-b border-white/10 p-4">
        <GcetLogo
          showText={true}
          title="GCET AI Assistant"
          subtitle="Academic Workspace"
          className="scale-90 origin-left"
        />
      </div>

      <nav className="flex-1 space-y-1.5 p-4">
        {displayMenu.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.title}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-xs font-semibold transition ${
                  isActive ? "bg-blue-600 text-white shadow-md shadow-blue-600/20" : "text-gray-300 hover:bg-white/10 hover:text-white"
                }`
              }
            >
              <Icon size={19} />
              {item.title}
            </NavLink>
          );
        })}
      </nav>

      <div className="border-t border-white/10 p-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-xl bg-red-600/90 px-3.5 py-2.5 text-xs font-semibold text-white transition hover:bg-red-600 shadow-md shadow-red-600/20 cursor-pointer"
        >
          <SignOut size={18} />
          Logout
        </button>
      </div>
    </aside>
  );
}