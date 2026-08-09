import Sidebar from "@/components/dashboard/Sidebar";
import Topbar from "@/components/dashboard/Topbar";

export default function DashboardLayout({ children }) {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#050816] text-white">
      <Sidebar />

      <div className="flex flex-1 flex-col lg:ml-56 min-w-0 h-screen overflow-hidden">
        <Topbar />

        <main className="flex-1 flex flex-col min-h-0 overflow-y-auto p-3 sm:p-5">
          {children}
        </main>
      </div>
    </div>
  );
}