import { Bell, MagnifyingGlass, User, List } from "@phosphor-icons/react";
import useProfile from "@/hooks/useProfile";

export default function Topbar({ onOpenMobileNav }) {
  const { data: profile } = useProfile();

  const displayName = profile?.full_name || profile?.email?.split("@")[0] || "GCET Student";
  const displayRole = profile?.role === "admin" ? "Administrator" : "Student";
  const initial = displayName.charAt(0).toUpperCase();

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/10 bg-[#050816]/95 px-3 sm:px-6 backdrop-blur-xl">
      <div className="flex items-center gap-3">
        {/* Mobile Hamburger Menu Button */}
        <button
          type="button"
          onClick={onOpenMobileNav}
          aria-label="Open navigation menu"
          className="flex size-9 items-center justify-center rounded-xl bg-[#0B1120] text-gray-300 border border-white/10 hover:bg-[#111827] hover:text-white lg:hidden transition cursor-pointer"
        >
          <List size={20} />
        </button>

        <div className="relative w-44 sm:w-72 md:w-96">
          <MagnifyingGlass
            size={18}
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"
          />
          <input
            placeholder="Search academic docs, topics, chats..."
            className="w-full rounded-xl border border-white/10 bg-[#0B1120] py-2 pl-10 pr-3 text-xs text-white outline-none placeholder:text-gray-400 focus:border-blue-500/50 transition"
          />
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        <button
          type="button"
          aria-label="Notifications"
          className="flex size-9 items-center justify-center rounded-xl bg-[#0B1120] text-gray-400 border border-white/10 hover:bg-[#111827] hover:text-white transition cursor-pointer"
        >
          <Bell size={18} />
        </button>

        <div className="flex items-center gap-3 border-l border-white/10 pl-3 sm:pl-4">
          <div className="flex size-9 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 text-sm font-bold text-white shadow-md">
            {initial || <User size={16} />}
          </div>

          <div className="hidden sm:block">
            <h3 className="text-xs font-bold text-white leading-tight">
              {displayName}
            </h3>
            <p className="text-[10px] font-medium text-emerald-400">
              {displayRole}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}