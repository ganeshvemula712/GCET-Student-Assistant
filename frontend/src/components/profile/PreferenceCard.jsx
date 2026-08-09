import { useState } from "react";
import { Sliders, Moon, Bell, Globe, Cpu } from "lucide-react";
import { toast } from "sonner";

export default function PreferenceCard() {
  const [emailNotifications, setEmailNotifications] = useState(true);

  const handleSavePreferences = () => {
    toast.success("Preferences updated.");
  };

  return (
    <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl sm:p-8">
      <div className="mb-6 flex items-center justify-between border-b border-gray-800/80 pb-4">
        <div>
          <h3 className="text-base font-bold text-white">System Preferences</h3>
          <p className="mt-0.5 text-xs text-gray-400">Configure theme, notifications, and AI model engine.</p>
        </div>
        <div className="flex size-8 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400">
          <Sliders size={16} />
        </div>
      </div>

      <div className="space-y-5 text-xs text-gray-300">
        {/* Theme */}
        <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3.5">
          <div className="flex items-center gap-3">
            <Moon size={16} className="text-indigo-400" />
            <div>
              <p className="font-bold text-white">Appearance Theme</p>
              <p className="text-[11px] text-gray-400">Dark AI SaaS (Default)</p>
            </div>
          </div>
          <span className="rounded-full bg-indigo-500/10 px-2.5 py-1 text-[10px] font-bold text-indigo-400 border border-indigo-500/20">
            Active Theme
          </span>
        </div>

        {/* Default AI Model */}
        <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3.5">
          <div className="flex items-center gap-3">
            <Cpu size={16} className="text-emerald-400" />
            <div>
              <p className="font-bold text-white">AI Engine Model</p>
              <p className="text-[11px] text-gray-400">Google Gemini 2.5 Flash + ChromaDB</p>
            </div>
          </div>
          <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-[10px] font-bold text-emerald-400 border border-emerald-500/20">
            RAG Grounding
          </span>
        </div>

        {/* Language */}
        <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3.5">
          <div className="flex items-center gap-3">
            <Globe size={16} className="text-cyan-400" />
            <div>
              <p className="font-bold text-white">Language</p>
              <p className="text-[11px] text-gray-400">English (United States)</p>
            </div>
          </div>
          <span className="text-gray-400 font-medium">Default</span>
        </div>

        {/* Notifications Toggle */}
        <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3.5">
          <div className="flex items-center gap-3">
            <Bell size={16} className="text-amber-400" />
            <div>
              <p className="font-bold text-white">Email Digest & Updates</p>
              <p className="text-[11px] text-gray-400">Receive weekly academic syllabus and chat summary tips</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => {
              setEmailNotifications((prev) => !prev);
              handleSavePreferences();
            }}
            className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
              emailNotifications ? "bg-emerald-500" : "bg-gray-800"
            }`}
          >
            <span
              className={`pointer-events-none inline-block size-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out ${
                emailNotifications ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </button>
        </div>
      </div>
    </div>
  );
}
