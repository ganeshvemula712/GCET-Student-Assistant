import { AnimatePresence, motion } from "framer-motion";
import { Outlet, useLocation, Link } from "react-router-dom";
import {
  GraduationCap,
  Home,
  MessageSquare,
  BookOpen,
  Calendar,
  Briefcase,
  ShieldCheck,
  Trophy,
  Info,
} from "lucide-react";

import AuthShowcase from "@/components/auth/AuthShowcase";

export default function AuthLayout({ children }) {
  const location = useLocation();

  const sidebarLinks = [
    { label: "Home", icon: Home, active: true, path: "/login" },
    { label: "Ask Assistant", icon: MessageSquare, path: "/login" },
    { label: "Resources", icon: BookOpen, path: "/login" },
    { label: "Attendance", icon: Calendar, path: "/login" },
    { label: "Placements", icon: Briefcase, path: "/login" },
    { label: "Regulations", icon: ShieldCheck, path: "/login" },
    { label: "NBA Info", icon: Trophy, path: "/login" },
    { label: "About GCET", icon: Info, path: "/login" },
  ];

  return (
    <div className="relative min-h-screen w-full bg-[#050914] font-[Inter,ui-sans-serif,system-ui,sans-serif] text-white flex flex-col justify-between selection:bg-indigo-600 selection:text-white overflow-x-hidden">
      {/* Top Header Mobile / Tablet */}
      <div className="flex items-center justify-between lg:hidden p-4 border-b border-gray-800/60 bg-[#070C1A]">
        <div className="flex items-center gap-2.5">
          <div className="flex size-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 text-white shadow-md">
            <GraduationCap size={20} />
          </div>
          <div className="flex flex-col leading-none">
            <span className="text-lg font-black text-amber-400">GCET</span>
            <span className="text-[10px] font-bold text-gray-300">Student Assistant</span>
          </div>
        </div>
      </div>

      <div className="flex flex-1 w-full max-w-[1720px] mx-auto min-w-0">
        {/* 1. LEFT NAVIGATION SIDEBAR (Matching Reference Image) */}
        <aside className="hidden lg:flex w-56 xl:w-64 flex-col justify-between border-r border-gray-800/60 bg-[#070C1A]/90 p-5 shrink-0 backdrop-blur-md">
          {/* Top Brand Logo Lockup */}
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-600 via-indigo-600 to-indigo-700 text-white shadow-lg shadow-purple-600/30">
                <GraduationCap size={22} />
              </div>
              <div className="flex flex-col leading-tight">
                <span className="text-xl font-black tracking-wide text-amber-400">
                  GCET
                </span>
                <span className="text-xs font-bold text-gray-300 tracking-tight">
                  Student Assistant
                </span>
              </div>
            </div>

            {/* Sidebar Navigation Items */}
            <nav className="space-y-1.5 pt-2">
              {sidebarLinks.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.label}
                    to={item.path}
                    className={`flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all duration-200 ${
                      item.active
                        ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
                        : "text-gray-400 hover:bg-gray-800/50 hover:text-white"
                    }`}
                  >
                    <Icon size={17} className={item.active ? "text-white" : "text-gray-400"} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Bottom Sidebar Tagline & Vector Illustration */}
          <div className="rounded-2xl border border-gray-800/60 bg-[#0A1022]/80 p-4 space-y-2.5">
            <div className="flex items-center justify-center py-1 opacity-70">
              <svg className="h-10 w-24 text-indigo-400" viewBox="0 0 100 40" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M10 35 V15 L30 5 L50 15 V35 M50 35 V20 L70 10 L90 20 V35" />
                <path d="M20 35 V22 M40 35 V22 M60 35 V25 M80 35 V25" />
              </svg>
            </div>
            <p className="text-[11px] font-semibold text-gray-400 leading-tight text-center">
              Your Questions. <br />
              <span className="text-amber-400">Our Knowledge.</span> <br />
              Better Tomorrow
            </p>
            <div className="w-10 h-0.5 bg-amber-400/80 mx-auto rounded-full" />
          </div>
        </aside>

        {/* 2. MAIN CENTER HERO SHOWCASE + RIGHT AUTH FORM */}
        <main className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_420px] xl:grid-cols-[1fr_440px] items-center gap-6 xl:gap-8 p-4 sm:p-6 lg:p-8 min-w-0">
          {/* Center Hero Showcase */}
          <AuthShowcase />

          {/* Right Authentication Card Section */}
          <div className="flex w-full items-center justify-center min-w-0 py-4 lg:py-0">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 10, scale: 0.99 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8, scale: 0.99 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="w-full flex justify-center min-w-0"
              >
                {children ?? <Outlet />}
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>

      {/* 3. FOOTER CREDIT BAR (Matching Reference Image) */}
      <footer className="w-full border-t border-gray-800/60 bg-[#070C1A]/80 px-6 py-3 text-center lg:text-left flex flex-col sm:flex-row items-center justify-between text-[11px] text-gray-400 font-medium gap-2">
        <div>
          GCET Student Assistant © 2026 – Built for GCET Students
        </div>
        <div className="flex items-center gap-1.5">
          <span>Made with</span>
          <span className="text-indigo-400">💜</span>
          <span>for GCET</span>
        </div>
      </footer>
    </div>
  );
}
