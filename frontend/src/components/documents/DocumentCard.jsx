import { memo } from "react";
import { FileText, Trash2, Layers, Database, Eye, ShieldCheck } from "lucide-react";

function DocumentCard({ document, onInspect, onDelete }) {
  const filename = document.filename || "GCET Document.pdf";
  const pages = document.page_count ?? 0;
  const chunks = document.chunk_count ?? 0;
  const status = document.status || "Ready";
  const isReady = status.toLowerCase() === "ready" || status.toLowerCase() === "processed" || status.toLowerCase() === "success";

  const uploadDate = document.uploaded_at
    ? new Date(document.uploaded_at).toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" })
    : "Recently";

  return (
    <div className="group relative flex flex-col justify-between rounded-2xl border border-gray-800 bg-[#111827] p-5 shadow-lg transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-500/40 hover:bg-[#151e30]">
      <div>
        <div className="flex items-start justify-between gap-3">
          <div className="flex size-11 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <FileText size={22} />
          </div>
          <span
            className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider border ${
              isReady
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                : "bg-cyan-500/10 text-cyan-400 border-cyan-500/20 animate-pulse"
            }`}
          >
            {status}
          </span>
        </div>

        <h3 className="mt-4 truncate text-sm font-bold text-white group-hover:text-emerald-400 transition-colors" title={filename}>
          {filename}
        </h3>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-1 rounded-lg border border-gray-800 bg-gray-900 px-2.5 py-1 text-[11px] font-medium text-gray-300">
            <Layers size={12} className="text-cyan-400" />
            {pages} pages
          </span>
          <span className="inline-flex items-center gap-1 rounded-lg border border-gray-800 bg-gray-900 px-2.5 py-1 text-[11px] font-medium text-gray-300">
            <Database size={12} className="text-purple-400" />
            {chunks} chunks
          </span>
        </div>
      </div>

      <div className="mt-5 border-t border-gray-800/80 pt-3">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span className="inline-flex items-center gap-1 text-[10px] font-medium text-emerald-400">
            <ShieldCheck size={12} /> ChromaDB
          </span>
          <span className="text-[10px] text-gray-500">{uploadDate}</span>
        </div>

        <div className="mt-3 flex items-center justify-between gap-2">
          <button
            type="button"
            onClick={() => onInspect?.(document)}
            className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-xl border border-gray-800 bg-gray-900 px-3 py-2 text-xs font-semibold text-gray-300 transition hover:border-emerald-500/40 hover:bg-emerald-500/10 hover:text-emerald-400"
          >
            <Eye size={14} />
            <span>Details</span>
          </button>

          <button
            type="button"
            onClick={() => onDelete?.(document)}
            className="flex size-9 items-center justify-center rounded-xl border border-gray-800 bg-gray-900 text-gray-400 transition hover:border-rose-500/40 hover:bg-rose-500/10 hover:text-rose-400"
            title="Delete Document"
          >
            <Trash2 size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default memo(DocumentCard);
