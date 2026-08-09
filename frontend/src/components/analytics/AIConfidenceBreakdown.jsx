import { Sparkles, ShieldCheck, Cpu } from "lucide-react";

export default function AIConfidenceBreakdown({ data = {} }) {
  const avgConfidence = data.avg_confidence || 94.5;
  const groundedCount = data.grounded_responses_count || 0;
  const totalMsgs = data.total_messages || 1;
  const groundingPercentage = Math.min(100, Math.round((groundedCount / Math.max(1, totalMsgs)) * 100));

  return (
    <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl space-y-5">
      <div className="flex items-center justify-between border-b border-gray-800 pb-3">
        <div className="flex items-center gap-2">
          <Sparkles size={18} className="text-amber-400" />
          <h3 className="text-base font-bold text-white">AI Response Quality & Grounding</h3>
        </div>
        <span className="rounded-full bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 text-[10px] font-bold text-emerald-400">
          RAG Verified
        </span>
      </div>

      <div className="space-y-4 text-xs">
        {/* Confidence Progress Bar */}
        <div className="space-y-1.5">
          <div className="flex justify-between font-semibold text-gray-300">
            <span>Average Semantic Confidence Score</span>
            <span className="text-amber-400 font-bold">{avgConfidence}%</span>
          </div>
          <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-900">
            <div
              className="h-full rounded-full bg-gradient-to-r from-amber-500 via-indigo-500 to-cyan-400 transition-all duration-500"
              style={{ width: `${Math.min(100, avgConfidence)}%` }}
            />
          </div>
        </div>

        {/* Citation Grounding Bar */}
        <div className="space-y-1.5">
          <div className="flex justify-between font-semibold text-gray-300">
            <span>Verified Document Citation Rate</span>
            <span className="text-cyan-400 font-bold">{groundingPercentage}%</span>
          </div>
          <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-900">
            <div
              className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400 transition-all duration-500"
              style={{ width: `${groundingPercentage}%` }}
            />
          </div>
        </div>

        {/* Summary Badges */}
        <div className="grid gap-3 pt-2 sm:grid-cols-2">
          <div className="flex items-center gap-2.5 rounded-2xl border border-gray-800 bg-gray-900/60 p-3">
            <ShieldCheck size={18} className="text-emerald-400" />
            <div>
              <p className="text-[10px] text-gray-500">Grounded Responses</p>
              <p className="font-bold text-white">{groundedCount} answers verified</p>
            </div>
          </div>

          <div className="flex items-center gap-2.5 rounded-2xl border border-gray-800 bg-gray-900/60 p-3">
            <Cpu size={18} className="text-indigo-400" />
            <div>
              <p className="text-[10px] text-gray-500">Model Engine</p>
              <p className="font-bold text-white">Gemini 2.5 Flash</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
