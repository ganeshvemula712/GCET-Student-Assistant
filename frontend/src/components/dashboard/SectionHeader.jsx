import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";

export default function SectionHeader({
  title,
  subtitle,
  icon: Icon,
  actionText,
  actionPath,
}) {
  return (
    <div className="mb-5 flex items-center justify-between">
      <div className="flex items-center gap-3">
        {Icon && (
          <div className="flex size-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400">
            <Icon size={20} />
          </div>
        )}
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white">{title}</h2>
          {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
        </div>
      </div>
      {actionText && actionPath && (
        <Link
          to={actionPath}
          className="flex items-center gap-1 text-xs font-medium text-emerald-400 transition hover:text-emerald-300 hover:underline"
        >
          {actionText} <ChevronRight size={14} />
        </Link>
      )}
    </div>
  );
}
