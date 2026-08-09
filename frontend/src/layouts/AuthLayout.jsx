import { AnimatePresence, motion } from "framer-motion";
import { Outlet, useLocation } from "react-router-dom";

import AuthShowcase from "@/components/auth/AuthShowcase";
import GcetLogo from "@/components/common/GcetLogo";

export default function AuthLayout({ children }) {
  const location = useLocation();

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#0B1220] font-[Inter,ui-sans-serif,system-ui,sans-serif] text-white">
      {/* Background Gradients & Mesh Accent */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_12%_12%,rgba(99,102,241,0.18),transparent_35%),radial-gradient(circle_at_85%_75%,rgba(6,182,212,0.15),transparent_38%)]" />
      <div className="absolute inset-0 opacity-20 [background-image:linear-gradient(rgba(99,102,241,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.06)_1px,transparent_1px)] [background-size:48px_48px]" />

      <div className="relative mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-center px-6 py-6 sm:px-10 sm:py-8 lg:grid lg:grid-cols-[57%_43%] lg:items-center lg:gap-8 xl:gap-12 lg:px-10 lg:py-8">
        {/* Mobile Header */}
        <div className="flex items-center justify-between lg:hidden mb-6">
          <GcetLogo showText={true} />
        </div>

        <AuthShowcase />

        <div className="flex flex-1 items-center justify-center py-4 lg:flex-none lg:justify-end lg:py-0 w-full">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, x: 16, scale: 0.985 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: -12, scale: 0.985 }}
              transition={{ duration: 0.24, ease: "easeOut" }}
              className="w-full flex justify-end"
            >
              {children ?? <Outlet />}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
