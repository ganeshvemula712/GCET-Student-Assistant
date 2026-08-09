import { BookOpen, CheckCircle2, Layers } from "lucide-react";
import SectionHeader from "./SectionHeader";

export default function KnowledgeSummary({ documents = [] }) {
  const totalDocuments = documents?.length ?? 0;
  const totalChunks =
    documents?.reduce((sum, doc) => sum + (doc.chunk_count || 0), 0) ?? 0;

  return (
    <div className="rounded-2xl border border-gray-800 bg-[#111827] p-6 shadow-xl">
      <SectionHeader
        title="Knowledge Base"
        subtitle="RAG index statistics"
        icon={BookOpen}
      />
      <div className="space-y-4">
        <div className="flex items-center justify-between rounded-xl border border-gray-800/80 bg-gray-900/50 p-3.5">
          <span className="text-xs font-medium text-gray-400">Indexed PDFs</span>
          <span className="text-sm font-bold text-white">{totalDocuments}</span>
        </div>
        <div className="flex items-center justify-between rounded-xl border border-gray-800/80 bg-gray-900/50 p-3.5">
          <span className="flex items-center gap-2 text-xs font-medium text-gray-400">
            <Layers size={14} className="text-cyan-400" /> Vector Chunks
          </span>
          <span className="text-sm font-bold text-cyan-400">{totalChunks}</span>
        </div>
        <div className="flex items-center justify-between rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-3.5">
          <span className="text-xs font-medium text-emerald-300">RAG Status</span>
          <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
            <CheckCircle2 size={15} /> Active
          </span>
        </div>
      </div>
    </div>
  );
}