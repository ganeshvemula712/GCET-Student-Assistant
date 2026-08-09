import { ShieldCheck, Activity } from "lucide-react";

export default function AdminHeader({ activeTab, onTabChange }) {
  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "users", label: "Users" },
    { id: "documents", label: "Documents" },
    { id: "conversations", label: "Conversations" },
    { id: "analytics", label: "AI Analytics" },
    { id: "health", label: "System Health" },
    { id: "audit", label: "Audit Logs" },
  ];

  return (
    <div className="space-y-6 border-b border-gray-800/80 pb-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="flex size-9 items-center justify-center rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <ShieldCheck size={20} />
            </div>
            <h1 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
              System Administration
            </h1>
          </div>
          <p className="mt-1 text-xs text-gray-400">
            Monitor system metrics, user roles, document vector indexes, AI model latency, and security logs.
          </p>
        </div>

        <div className="inline-flex items-center gap-2 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-3.5 py-2 text-xs font-semibold text-emerald-400">
          <Activity size={16} className="animate-pulse" />
          <span>All Services Operational</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-t border-gray-800/80 pt-4">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`rounded-2xl px-4 py-2 text-xs font-semibold transition ${
                isActive
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20"
                  : "bg-gray-900/60 text-gray-400 hover:bg-gray-800 hover:text-white"
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
