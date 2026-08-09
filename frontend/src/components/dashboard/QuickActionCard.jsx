import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";

export default function QuickActionCard({
  title,
  description,
  icon: Icon,
  to,
  badge,
  index = 0,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
    >
      <Link
        to={to}
        className="group relative flex flex-col justify-between rounded-2xl border border-gray-800 bg-[#111827] p-6 shadow-xl transition-all duration-300 hover:-translate-y-1 hover:border-emerald-500/40 hover:bg-[#151e30] hover:shadow-2xl hover:shadow-emerald-500/5"
      >
        <div className="flex items-start justify-between">
          <div className="flex size-12 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-400 transition-colors duration-300 group-hover:bg-emerald-500 group-hover:text-gray-950">
            <Icon size={24} />
          </div>
          <div className="flex size-8 items-center justify-center rounded-full border border-gray-800 bg-gray-900/60 text-gray-400 transition-colors duration-300 group-hover:border-emerald-500/40 group-hover:text-emerald-400">
            <ArrowUpRight size={16} />
          </div>
        </div>
        <div className="mt-5">
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-white transition-colors duration-300 group-hover:text-emerald-400">
              {title}
            </h3>
            {badge && (
              <span className="rounded-full bg-cyan-500/10 px-2 py-0.5 text-[10px] font-semibold text-cyan-300 border border-cyan-500/20">
                {badge}
              </span>
            )}
          </div>
          <p className="mt-1 text-xs text-gray-400 line-clamp-2">{description}</p>
        </div>
      </Link>
    </motion.div>
  );
}
