import { Sparkles, BookOpen } from "lucide-react";

export default function EmptyDocuments() {
  return (
    <div className="flex flex-col items-center justify-center rounded-3xl border border-gray-800 bg-[#111827] p-12 text-center shadow-xl">
      <div className="flex size-16 items-center justify-center rounded-3xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 text-emerald-400 border border-emerald-500/30">
        <BookOpen size={32} />
      </div>

      <h3 className="mt-6 text-xl font-bold text-white">No Knowledge Base Documents</h3>
      <p className="mt-2 text-xs text-gray-400 max-w-md leading-relaxed">
        Your GCET AI Assistant knowledge vector store is empty. Upload your first PDF syllabus, college regulation guide, or previous question paper above to empower RAG grounding.
      </p>

      <div className="mt-6 flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-xs font-semibold text-emerald-400">
        <Sparkles size={14} />
        <span>ChromaDB Vector Retrieval Engine Ready</span>
      </div>
    </div>
  );
}