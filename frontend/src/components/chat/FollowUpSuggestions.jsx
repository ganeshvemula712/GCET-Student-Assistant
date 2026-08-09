import { Sparkles, ArrowRight } from "lucide-react";

export default function FollowUpSuggestions({ suggestions = [], onSelect }) {
  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="mt-6 border-t border-gray-800/80 pt-4">
      <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
        <Sparkles size={14} /> Suggested Follow-up Questions
      </div>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            type="button"
            onClick={() => onSelect?.(suggestion)}
            className="group inline-flex items-center gap-2 rounded-xl border border-gray-800 bg-[#0f172a] px-3.5 py-2 text-xs font-medium text-gray-300 transition-all duration-200 hover:border-emerald-500/40 hover:bg-[#131d33] hover:text-white"
          >
            <span>{suggestion}</span>
            <ArrowRight size={12} className="text-gray-500 transition-transform duration-200 group-hover:translate-x-0.5 group-hover:text-emerald-400" />
          </button>
        ))}
      </div>
    </div>
  );
}
