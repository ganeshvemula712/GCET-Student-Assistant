import { MessageSquare, FileText, Bot, PlusCircle } from "lucide-react";

export default function ActivityItem({
  type = "chat",
  title,
  subtitle,
  time,
  status = "Completed",
}) {
  const config = {
    chat: {
      icon: MessageSquare,
      color: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    },
    upload: {
      icon: FileText,
      color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    },
    response: {
      icon: Bot,
      color: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    },
    created: {
      icon: PlusCircle,
      color: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    },
  }[type] || {
    icon: MessageSquare,
    color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  };

  const Icon = config.icon;

  return (
    <div className="group relative flex items-start gap-4 rounded-xl border border-gray-800/80 bg-[#111827]/60 p-4 transition-all duration-200 hover:border-gray-700 hover:bg-[#111827]">
      <div
        className={`flex size-10 shrink-0 items-center justify-center rounded-xl border ${config.color}`}
      >
        <Icon size={18} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <p className="truncate text-sm font-semibold text-white group-hover:text-emerald-400">
            {title}
          </p>
          <span className="shrink-0 text-[11px] text-gray-500">{time}</span>
        </div>
        {subtitle && (
          <p className="mt-0.5 truncate text-xs text-gray-400">{subtitle}</p>
        )}
      </div>
      {status && (
        <span className="shrink-0 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-400 border border-emerald-500/20">
          {status}
        </span>
      )}
    </div>
  );
}
