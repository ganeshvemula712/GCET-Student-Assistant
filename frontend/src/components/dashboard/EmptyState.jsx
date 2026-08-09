import { FolderOpen, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function EmptyState({
  title = "No data found",
  description = "Get started by creating your first item.",
  actionText,
  actionPath,
  icon: Icon = FolderOpen,
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-800 bg-[#111827]/40 p-8 text-center">
      <div className="flex size-12 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-400">
        <Icon size={24} />
      </div>
      <h3 className="mt-4 text-lg font-semibold text-white">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-gray-400">{description}</p>
      {actionText && actionPath && (
        <Link
          to={actionPath}
          className="mt-5 inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-4 py-2 text-xs font-semibold text-gray-950 transition hover:bg-emerald-400"
        >
          {actionText} <ArrowRight size={14} />
        </Link>
      )}
    </div>
  );
}
