import { Bot, Sparkles, Menu, Plus } from "lucide-react";

export default function ChatHeader({ onToggleSidebar, onNewChat, totalMessages = 0 }) {
  return (
    <div className="sticky top-0 z-10 flex items-center justify-between border-b border-gray-800 bg-[#0B1220]/95 px-6 py-4 backdrop-blur-md">
      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            type="button"
            onClick={onToggleSidebar}
            className="flex size-9 items-center justify-center rounded-xl border border-gray-800 text-gray-400 md:hidden hover:bg-gray-800 hover:text-white"
            title="Toggle conversations sidebar"
          >
            <Menu size={18} />
          </button>
        )}
        <div className="flex size-10 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-500 text-gray-950 shadow-md">
          <Bot size={22} />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold text-white">GCET AI Assistant</h2>
            <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/20">
              Gemini 3.5 Flash
            </span>
          </div>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="size-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-gray-400">RAG Knowledge Engine Active</span>
            {totalMessages > 0 && (
              <>
                <span className="text-gray-600">•</span>
                <span className="text-xs text-gray-400">{totalMessages} messages</span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {onNewChat && (
          <button
            type="button"
            onClick={onNewChat}
            className="flex items-center gap-1.5 rounded-xl border border-gray-800 bg-gray-900/80 px-3.5 py-2 text-xs font-semibold text-gray-300 transition-colors hover:border-emerald-500/40 hover:bg-emerald-500/10 hover:text-emerald-400"
          >
            <Plus size={15} />
            <span className="hidden sm:inline">New Chat</span>
          </button>
        )}
        <div className="flex size-9 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400">
          <Sparkles size={18} />
        </div>
      </div>
    </div>
  );
}