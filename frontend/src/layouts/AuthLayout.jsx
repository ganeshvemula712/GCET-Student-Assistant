import { AnimatePresence, motion } from "framer-motion";
import { Outlet, useLocation } from "react-router-dom";

import AuthShowcase from "@/components/auth/AuthShowcase";
import GcetLogo from "@/components/common/GcetLogo";

export default function AuthLayout({ children }) {
  const location = useLocation();

  return (
    <div className="relative min-h-screen w-full overflow-x-hidden bg-[#050816] font-[Inter,ui-sans-serif,system-ui,sans-serif] text-white flex flex-col justify-center items-center py-6 px-4 sm:px-8 selection:bg-indigo-500 selection:text-white">
      {/* Background Gradients & Ambient Accents */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_12%_12%,rgba(99,102,241,0.15),transparent_35%),radial-gradient(circle_at_85%_75%,rgba(6,182,212,0.12),transparent_38%)] pointer-events-none" />
      <div className="absolute inset-0 opacity-15 [background-image:linear-gradient(rgba(99,102,241,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.06)_1px,transparent_1px)] [background-size:48px_48px] pointer-events-none" />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-center py-4 lg:grid lg:grid-cols-[57%_43%] lg:items-center lg:gap-8 xl:gap-12 min-w-0">
        {/* Mobile / Tablet Header */}
        <div className="flex items-center justify-center lg:hidden mb-6">
          <GcetLogo showText={true} />
        </div>

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
    </div>
  );
}
