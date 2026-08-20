import { useState } from "react";
import { useLocation } from "react-router-dom";
import Sidebar from "@/components/dashboard/Sidebar";
import Topbar from "@/components/dashboard/Topbar";
import MobileNavDrawer from "@/components/dashboard/MobileNavDrawer";

export default function DashboardLayout({ children }) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const location = useLocation();
  const isChatPage = location.pathname === "/chat";

  return (
    <div className="flex h-screen h-[100dvh] w-screen overflow-hidden bg-[#050816] text-white">
      <Sidebar />
      <MobileNavDrawer open={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />

      <div className="flex flex-1 flex-col lg:ml-56 min-w-0 h-screen h-[100dvh] overflow-hidden">
        <Topbar onOpenMobileNav={() => setMobileNavOpen(true)} />

        <main className={`flex-1 flex flex-col min-h-0 ${isChatPage ? "overflow-hidden" : "overflow-y-auto"} p-2 sm:p-4 lg:p-5`}>
          {children}
        </main>
      </div>
    </div>
  );
}