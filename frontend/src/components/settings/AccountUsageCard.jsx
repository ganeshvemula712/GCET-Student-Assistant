import { ShieldCheck, Database, HardDrive, KeyRound } from "lucide-react";

export default function AccountUsageCard() {
  return (
    <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-gray-800 pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck size={18} className="text-emerald-400" />
          <h3 className="text-base font-bold text-white">Account Workspace Usage</h3>
        </div>
        <span className="rounded-full bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 text-[10px] font-bold text-emerald-400">
          Student Enterprise Plan
        </span>
      </div>

      <div className="grid gap-4 sm:grid-cols-3 text-xs">
        <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-4 space-y-1">
          <div className="flex items-center gap-2 text-indigo-400 font-semibold">
            <KeyRound size={16} />
            <span>Authentication Token</span>
          </div>
          <p className="text-base font-bold text-white">OAuth2 Bearer JWT</p>
          <p className="text-[11px] text-gray-400">60-minute expiration cycle</p>
        </div>

        <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-4 space-y-1">
          <div className="flex items-center gap-2 text-cyan-400 font-semibold">
            <Database size={16} />
            <span>Knowledge Base Index</span>
          </div>
          <p className="text-base font-bold text-white">ChromaDB Vector Store</p>
          <p className="text-[11px] text-gray-400">Indexed course documents</p>
        </div>

        <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-4 space-y-1">
          <div className="flex items-center gap-2 text-purple-400 font-semibold">
            <HardDrive size={16} />
            <span>Storage Quota</span>
          </div>
          <p className="text-base font-bold text-white">50 MB / Unlimited</p>
          <p className="text-[11px] text-gray-400">PDF document repository</p>
        </div>
      </div>
    </div>
  );
}
