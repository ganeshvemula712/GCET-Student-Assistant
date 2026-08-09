import { motion } from "framer-motion";
import CountUpModule from "react-countup";

const CountUp = typeof CountUpModule === "function"
  ? CountUpModule
  : (typeof CountUpModule?.default === "function" ? CountUpModule.default : null);

export default function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  badgeText,
  color = "emerald",
  index = 0,
}) {
  const isNumber = typeof value === "number";

  const colorStyles = {
    emerald: {
      bg: "bg-emerald-500/10",
      text: "text-emerald-400",
      border: "border-emerald-500/20",
    },
    cyan: {
      bg: "bg-cyan-500/10",
      text: "text-cyan-400",
      border: "border-cyan-500/20",
    },
    purple: {
      bg: "bg-purple-500/10",
      text: "text-purple-400",
      border: "border-purple-500/20",
    },
    amber: {
      bg: "bg-amber-500/10",
      text: "text-amber-400",
      border: "border-amber-500/20",
    },
  }[color] || {
    bg: "bg-emerald-500/10",
    text: "text-emerald-400",
    border: "border-emerald-500/20",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="group relative overflow-hidden rounded-2xl border border-gray-800 bg-[#111827] p-6 shadow-xl transition-all duration-300 hover:border-gray-700"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-gray-400">
            {title}
          </p>
          <div className="mt-3 text-3xl font-bold tracking-tight text-white">
            {isNumber ? (
              CountUp ? (
                <CountUp end={value} duration={1.5} separator="," />
              ) : (
                value.toLocaleString()
              )
            ) : (
              value
            )}
          </div>
          {subtitle && (
            <p className="mt-2 text-xs text-gray-400">{subtitle}</p>
          )}
        </div>
        {Icon && (
          <div
            className={`flex size-12 items-center justify-center rounded-2xl ${colorStyles.bg} ${colorStyles.text} transition-transform duration-300 group-hover:scale-110`}
          >
            <Icon size={24} />
          </div>
        )}
      </div>
      {badgeText && (
        <div className="mt-4 inline-flex items-center gap-1 rounded-full border border-gray-800 bg-gray-900/80 px-2.5 py-1 text-[10px] font-medium text-gray-300">
          <span className="size-1.5 rounded-full bg-emerald-400" />
          {badgeText}
        </div>
      )}
    </motion.div>
  );
}
