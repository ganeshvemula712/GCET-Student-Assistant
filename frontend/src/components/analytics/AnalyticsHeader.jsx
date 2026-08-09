import { BarChart3, Activity } from "lucide-react";

export default function AnalyticsHeader({ days, onDaysChange }) {
  const timeframes = [
    { value: 7, label: "7 Days" },
    { value: 30, label: "30 Days" },
    { value: 90, label: "90 Days" },
  ];

  return (
    <div className="flex flex-col gap-4 border-b border-gray-800/80 pb-6 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex items-center gap-2.5">
          <div className="flex size-9 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <BarChart3 size={20} />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
            Platform & AI Analytics
          </h1>
        </div>
        <p className="mt-1 text-xs text-gray-400">
          Real-time metrics tracking student engagement, RAG response confidence, vector indexing, and conversation trends.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1 rounded-2xl border border-gray-800 bg-gray-900/80 p-1">
          {timeframes.map((tf) => (
            <button
              key={tf.value}
              onClick={() => onDaysChange(tf.value)}
              className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition ${
                days === tf.value
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {tf.label}
            </button>
          ))}
        </div>

        <div className="hidden sm:inline-flex items-center gap-2 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-3.5 py-2 text-xs font-semibold text-emerald-400">
          <Activity size={15} className="animate-pulse" />
          <span>Real-time DB Sync</span>
        </div>
      </div>
    </div>
  );
}
