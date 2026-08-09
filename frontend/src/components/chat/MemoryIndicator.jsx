import { Brain, Sparkles } from "lucide-react";

export default function MemoryIndicator({ messageCount = 0, retrievedCount = 0 }) {
  return (
    <div className="mb-4 flex items-center justify-between rounded-xl border border-gray-800/80 bg-[#0f172a]/70 px-4 py-2 text-xs text-gray-300 backdrop-blur-sm">
      <div className="flex items-center gap-2">
        <Brain size={15} className="text-emerald-400" />
        <span className="font-semibold text-white">Conversation Memory Active</span>
        <span className="text-gray-500">•</span>
        <span className="text-gray-400">{messageCount} messages remembered</span>
      </div>
      <div className="hidden sm:flex items-center gap-2 text-[11px] text-gray-400">
        <Sparkles size={13} className="text-cyan-400" />
        <span>{retrievedCount > 0 ? `${retrievedCount} RAG docs grounded` : "RAG Context: 4,096 tokens"}</span>
      </div>
    </div>
  );
}
