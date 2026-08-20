import { useState } from "react";
import { Info, Clock, Cpu, FileText, Zap, ChevronDown, ChevronUp } from "lucide-react";

export default function AIMetadataBar({
  confidence = 0,
  sourcesCount = 0,
  content = "",
  model = "Gemini 3.5 Flash",
}) {
  const [expanded, setExpanded] = useState(false);
  const wordCount = content ? content.trim().split(/\s+/).length : 0;
  const estimatedTime = Math.max(1, Math.round(wordCount / 20)) / 10; // estimated seconds

  return (
    <div className="mt-4 border-t border-gray-800/60 pt-3">
      <button
        type="button"
        onClick={() => setExpanded((prev) => !prev)}
        className="flex items-center gap-2 text-[11px] font-medium text-gray-400 hover:text-white transition-colors"
      >
        <Info size={13} className="text-cyan-400" />
        <span>AI Response Metadata</span>
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {expanded && (
        <div className="mt-2.5 grid grid-cols-2 gap-2 rounded-xl border border-gray-800/80 bg-gray-950/60 p-3 text-[11px] text-gray-300 sm:grid-cols-4">
          <div className="flex items-center gap-1.5">
            <Cpu size={13} className="text-emerald-400 shrink-0" />
            <div>
              <p className="text-[10px] text-gray-500">Model Engine</p>
              <p className="font-semibold text-white">{model} ({confidence}%)</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <FileText size={13} className="text-cyan-400 shrink-0" />
            <div>
              <p className="text-[10px] text-gray-500">Grounded Sources</p>
              <p className="font-semibold text-white">{sourcesCount} Documents</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <Zap size={13} className="text-amber-400 shrink-0" />
            <div>
              <p className="text-[10px] text-gray-500">Response Size</p>
              <p className="font-semibold text-white">{wordCount} words</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <Clock size={13} className="text-purple-400 shrink-0" />
            <div>
              <p className="text-[10px] text-gray-500">Est. Latency</p>
              <p className="font-semibold text-white">~{estimatedTime}s</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
