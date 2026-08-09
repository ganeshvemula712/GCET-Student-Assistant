import { User, ShieldCheck } from "lucide-react";

export default function ProfileHeader() {
  return (
    <div className="flex flex-col gap-2 border-b border-gray-800/80 pb-6 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex items-center gap-2.5">
          <div className="flex size-9 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <User size={20} />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
            Account & Settings
          </h1>
        </div>
        <p className="mt-1 text-xs text-gray-400">
          Manage your student profile, academic credentials, security preferences, and workspace settings.
        </p>
      </div>

      <div className="inline-flex items-center gap-2 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-3.5 py-2 text-xs font-semibold text-emerald-400">
        <ShieldCheck size={16} />
        <span>Verified Student Account</span>
      </div>
    </div>
  );
}
