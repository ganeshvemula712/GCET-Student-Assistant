import { Cpu, HelpCircle } from "lucide-react";

export default function AIAnalyticsCard() {
  const topQuestions = [
    { question: "What are the minimum attendance requirements for R22 semester exams?", count: 86 },
    { question: "Explain the eligibility criteria for campus placement drives.", count: 64 },
    { question: "How to apply for revaluation of mid-term examination marks?", count: 52 },
    { question: "What is the syllabus structure for CSE Data Structures course?", count: 41 },
  ];

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* AI Performance Breakdown */}
      <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div className="flex items-center gap-2">
            <Cpu size={18} className="text-indigo-400" />
            <h3 className="text-base font-bold text-white">AI Engine Performance</h3>
          </div>
          <span className="rounded-full bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 text-[10px] font-bold text-emerald-400">
            Gemini 3.5 Flash
          </span>
        </div>

        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3">
            <span className="text-gray-400">Total API Prompt Requests</span>
            <span className="font-bold text-white">1,420 Prompts</span>
          </div>

          <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3">
            <span className="text-gray-400">Average Token Response Latency</span>
            <span className="font-bold text-cyan-400">420 ms</span>
          </div>

          <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3">
            <span className="text-gray-400">Total Tokens Generated</span>
            <span className="font-bold text-indigo-400">284,500 Tokens</span>
          </div>

          <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3">
            <span className="text-gray-400">Grounding Citation Accuracy</span>
            <span className="font-bold text-emerald-400">96.8% Verified</span>
          </div>
        </div>
      </div>

      {/* Top Student Queries */}
      <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div className="flex items-center gap-2">
            <HelpCircle size={18} className="text-cyan-400" />
            <h3 className="text-base font-bold text-white">Most Asked Academic Questions</h3>
          </div>
          <span className="text-xs text-gray-400">Top 4</span>
        </div>

        <div className="space-y-3">
          {topQuestions.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between gap-3 rounded-2xl border border-gray-800 bg-gray-900/60 p-3 text-xs">
              <span className="text-gray-300 truncate">{item.question}</span>
              <span className="shrink-0 rounded-full bg-indigo-500/10 px-2.5 py-0.5 font-bold text-indigo-400 border border-indigo-500/20">
                {item.count} asks
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
