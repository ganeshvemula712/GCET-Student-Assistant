import { useEffect } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
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
  X,
} from "@phosphor-icons/react";
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

export default function MobileNavDrawer({ open, onClose }) {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { data: profile } = useProfile();

  // Close on Escape key press
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === "Escape" && open) {
        onClose();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  // Prevent background body scroll when drawer is open on mobile
  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  function handleLogout() {
    onClose();
    logout();
    toast.success("Logged out successfully.");
    navigate("/");
  }

  const isAdmin = profile?.role === "admin";
  const displayMenu = menu.filter((item) => item.path !== "/admin" || isAdmin);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true" aria-label="Mobile navigation menu">
          {/* Backdrop Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Drawer Sidebar Content */}
          <motion.aside
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 250 }}
            className="fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col border-r border-white/10 bg-[#0B1120] text-white shadow-2xl"
          >
            {/* Drawer Header */}
            <div className="flex items-center justify-between border-b border-white/10 p-4">
              <GcetLogo
                showText={true}
                title="GCET AI Assistant"
                subtitle="Academic Workspace"
                className="scale-90 origin-left"
              />
              <button
                type="button"
                onClick={onClose}
                aria-label="Close navigation menu"
                className="flex size-9 items-center justify-center rounded-xl bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10 hover:text-white transition"
              >
                <X size={20} />
              </button>
            </div>

            {/* Role Badge Pill */}
            <div className="px-4 pt-3 pb-1">
              <div className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-[11px] font-semibold text-emerald-400">
                <span>Role: {isAdmin ? "Administrator" : "Student"}</span>
              </div>
            </div>

            {/* Navigation Menu Links */}
            <nav className="flex-1 space-y-1.5 overflow-y-auto p-4">
              {displayMenu.map((item) => {
                const Icon = item.icon;

                return (
                  <NavLink
                    key={item.title}
                    to={item.path}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `flex items-center gap-3.5 rounded-xl px-4 py-3 text-sm font-semibold transition ${
                        isActive
                          ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
                          : "text-gray-300 hover:bg-white/10 hover:text-white"
                      }`
                    }
                  >
                    <Icon size={20} />
                    <span>{item.title}</span>
                  </NavLink>
                );
              })}
            </nav>

            {/* Logout Footer */}
            <div className="border-t border-white/10 p-4">
              <button
                type="button"
                onClick={handleLogout}
                className="flex w-full items-center justify-center gap-3 rounded-xl bg-red-600/90 px-4 py-3 text-sm font-semibold text-white transition hover:bg-red-600 shadow-md shadow-red-600/20 cursor-pointer"
              >
                <SignOut size={20} />
                <span>Logout</span>
              </button>
            </div>
          </motion.aside>
        </div>
      )}
    </AnimatePresence>
  );
}
