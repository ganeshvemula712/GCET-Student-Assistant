import { FileText, ExternalLink } from "lucide-react";

export default function SourceCard({ source, onOpen }) {
  const filename = source?.filename || "College Document.pdf";
  const page = source?.page ?? 1;
  const preview = source?.chunk_preview || source?.preview || "Verified GCET Knowledge Base content chunk.";

  return (
    <button
      type="button"
      onClick={() => onOpen?.(source)}
      className="group flex w-full flex-col justify-between rounded-xl border border-gray-800 bg-[#0f172a]/90 p-3.5 text-left transition-all duration-200 hover:border-emerald-500/40 hover:bg-[#131d33] hover:shadow-lg"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400">
            <FileText size={15} />
          </div>
          <p className="truncate text-xs font-semibold text-white group-hover:text-emerald-400">
            {filename}
          </p>
        </div>
        <span className="shrink-0 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-2 py-0.5 text-[10px] font-medium text-cyan-300">
          Page {page}
        </span>
      </div>
      <p className="mt-2.5 line-clamp-2 text-xs leading-relaxed text-gray-400">
        {preview}
      </p>
      <div className="mt-2.5 flex items-center justify-end text-[10px] font-medium text-emerald-400 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
        <span>Inspect Source</span>
        <ExternalLink size={10} className="ml-1" />
      </div>
    </button>
  );
}
