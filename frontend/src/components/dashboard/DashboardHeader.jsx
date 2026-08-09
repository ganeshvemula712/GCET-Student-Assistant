import { Sparkles, Bot, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

export default function DashboardHeader() {
  const hour = new Date().getHours();
  let greeting = "Hello";
  if (hour < 12) greeting = "Good Morning";
  else if (hour < 17) greeting = "Good Afternoon";
  else greeting = "Good Evening";

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="relative overflow-hidden rounded-3xl border border-gray-800 bg-gradient-to-r from-[#111827] via-[#131e32] to-[#111827] p-8 shadow-2xl"
    >
      <div className="absolute right-0 top-0 -mr-16 -mt-16 size-64 rounded-full bg-emerald-500/5 blur-3xl" />
      <div className="relative flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400">
            <Sparkles size={14} /> AI Academic Workstation
          </div>
          <h1 className="mt-3 text-3xl font-extrabold tracking-tight text-white md:text-4xl">
            {greeting}, Student 👋
          </h1>
          <p className="mt-2 max-w-xl text-sm leading-relaxed text-gray-400">
            Welcome to your intelligent workspace. Query GCET regulations, inspect course documents, and prepare for placement drives.
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <Link
            to="/chat"
            className="group flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-3 text-sm font-bold text-gray-950 shadow-lg shadow-emerald-500/20 transition-all duration-300 hover:bg-emerald-400 hover:shadow-emerald-500/30"
          >
            <Bot size={18} /> Ask AI Assistant{" "}
            <ArrowRight size={16} className="transition-transform duration-300 group-hover:translate-x-1" />
          </Link>
        </div>
      </div>
    </motion.div>
  );
}