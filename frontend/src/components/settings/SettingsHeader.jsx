import { Gear, ShieldCheck } from "@phosphor-icons/react";

export default function SettingsHeader() {
  return (
    <div className="flex flex-col gap-2 border-b border-gray-800/80 pb-6 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex items-center gap-2.5">
          <div className="flex size-9 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Gear size={22} />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
            Workspace Settings
          </h1>
        </div>
        <p className="mt-1 text-xs text-gray-400">
          Configure security credentials, notification digests, AI assistant preferences, and active session tokens.
        </p>
      </div>

      <div className="inline-flex items-center gap-2 rounded-2xl border border-indigo-500/20 bg-indigo-500/10 px-3.5 py-2 text-xs font-semibold text-indigo-300">
        <ShieldCheck size={16} />
        <span>JWT Session Active</span>
      </div>
    </div>
  );
}
