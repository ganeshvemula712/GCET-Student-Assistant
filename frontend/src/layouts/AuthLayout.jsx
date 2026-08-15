import { AnimatePresence, motion } from "framer-motion";
import { Outlet, useLocation } from "react-router-dom";

import AuthShowcase from "@/components/auth/AuthShowcase";
import GcetLogo from "@/components/common/GcetLogo";
import gcetCampusImg from "@/assets/images/gcet-campus.jpg";

export default function AuthLayout({ children }) {
  const location = useLocation();

  return (
    <div className="relative min-h-screen w-full overflow-x-hidden bg-[#050816] font-[Inter,ui-sans-serif,system-ui,sans-serif] text-white flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      {/* 1. CINEMATIC GCET CAMPUS HERO COMPOSITION (Left Showcase Side) */}
      <div className="absolute inset-y-0 left-0 w-full lg:w-[65%] overflow-hidden pointer-events-none z-0">
        <img
          src={gcetCampusImg}
          alt="GCET Campus Building"
          className="h-full w-full object-cover object-[70%_25%] sm:object-[75%_25%] lg:object-[78%_25%] opacity-90 sm:opacity-95 filter brightness-[1.05] contrast-[1.08] saturate-[1.15]"
        />
        {/* Left Dark Gradient Mask: Ensures top-left logo & hero headline text have 100% crisp contrast */}
        <div className="absolute inset-y-0 left-0 w-[55%] bg-gradient-to-r from-[#050816] via-[#050816]/75 to-transparent" />
        {/* Right Gradient Mask: Smoothly fades campus visual to solid dark navy before right authentication card */}
        <div className="absolute inset-y-0 right-0 w-[40%] bg-gradient-to-l from-[#050816] via-[#050816]/60 to-transparent" />
        {/* Top & Bottom Vignettes for vertical framing */}
        <div className="absolute top-0 inset-x-0 h-24 bg-gradient-to-b from-[#050816]/80 to-transparent" />
        <div className="absolute bottom-0 inset-x-0 h-32 bg-gradient-to-t from-[#050816] via-[#050816]/70 to-transparent" />
      </div>

      {/* 2. Ambient Accent Glows */}
      <div className="absolute top-1/4 left-1/4 size-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none z-0" />
      <div className="absolute bottom-1/3 right-1/4 size-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none z-0" />

      {/* 3. MAIN CONTENT CONTAINER */}
      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-7xl flex-col justify-between p-4 sm:p-6 lg:p-8 min-w-0">
        {/* Top Mobile / Tablet Header */}
        <div className="flex items-center justify-center lg:hidden my-4">
          <GcetLogo showText={true} />
        </div>

        {/* Center Grid Layout: 57% Hero Showcase | 43% Authentication Card */}
        <div className="my-auto grid w-full grid-cols-1 lg:grid-cols-[57%_43%] lg:items-center lg:gap-8 xl:gap-12 min-w-0 py-4">
          {/* Left Hero Column */}
          <AuthShowcase />

          {/* Right Auth Form Column */}
          <div className="flex w-full items-center justify-center py-4 lg:py-0 min-w-0">
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
        </div>

        {/* 4. FOOTER CREDITS (Matching Reference Bottom Bar) */}
        <footer className="w-full pt-4 pb-2 border-t border-gray-800/40 text-center lg:text-left flex flex-col sm:flex-row items-center justify-between text-[11px] text-gray-400 gap-2 font-medium">
          <div>
            © 2026 GCET Student Assistant. All rights reserved.
          </div>
          <div className="flex items-center gap-1.5">
            <span>Made with</span>
            <span className="text-indigo-400">💜</span>
            <span>for GCET</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
