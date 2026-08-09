import { FileText, Database, Layers, Sparkles } from "lucide-react";

export default function DocumentHeader({ documents = [] }) {
  const totalPages = documents.reduce((sum, d) => sum + (d.page_count || 0), 0);
  const totalChunks = documents.reduce((sum, d) => sum + (d.chunk_count || 0), 0);
  const readyCount = documents.filter((d) => d.status?.toLowerCase() === "ready" || d.status?.toLowerCase() === "processed" || d.status?.toLowerCase() === "success").length;

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-gray-800/80 pb-6">
      <div>
        <div className="flex items-center gap-2">
          <div className="flex size-9 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400">
            <FileText size={20} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
            Knowledge Base Documents
          </h1>
        </div>
        <p className="mt-1.5 text-xs text-gray-400">
          Upload and manage GCET study materials, regulations, and syllabus files indexed into ChromaDB vector storage.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 rounded-2xl border border-gray-800 bg-[#111827] px-3.5 py-2 text-xs">
          <FileText size={15} className="text-emerald-400" />
          <span className="text-gray-400">Docs:</span>
          <strong className="text-white">{documents.length}</strong>
        </div>

        <div className="flex items-center gap-2 rounded-2xl border border-gray-800 bg-[#111827] px-3.5 py-2 text-xs">
          <Layers size={15} className="text-cyan-400" />
          <span className="text-gray-400">Pages:</span>
          <strong className="text-white">{totalPages}</strong>
        </div>

        <div className="flex items-center gap-2 rounded-2xl border border-gray-800 bg-[#111827] px-3.5 py-2 text-xs">
          <Database size={15} className="text-purple-400" />
          <span className="text-gray-400">Chunks:</span>
          <strong className="text-white">{totalChunks}</strong>
        </div>

        <div className="flex items-center gap-2 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-3.5 py-2 text-xs">
          <Sparkles size={15} className="text-emerald-400" />
          <span className="text-emerald-300">Vector Ready:</span>
          <strong className="text-emerald-400">{readyCount}</strong>
        </div>
      </div>
    </div>
  );
}