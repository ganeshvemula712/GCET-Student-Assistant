import { X, FileText, Copy, Check, ShieldCheck } from "lucide-react";
import { useState } from "react";

export default function SourceModal({ open, source, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!open || !source) {
    return null;
  }

  const filename = source.filename || "GCET Knowledge Document.pdf";
  const page = source.page ?? 1;
  const chunkIndex = source.chunk_index ?? source.chunk ?? 1;
  const score = source.distance ? Math.max(0, Math.round((1 - source.distance) * 100)) : 92;
  const content = source.chunk_preview || source.preview || source.text || "No preview text available for this chunk.";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-md">
      <div className="relative w-full max-w-2xl overflow-hidden rounded-3xl border border-gray-800 bg-[#111827] shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-800 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400">
              <FileText size={20} />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">{filename}</h3>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <span>Page {page}</span>
                <span>•</span>
                <span>Chunk #{chunkIndex}</span>
                <span>•</span>
                <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold">
                  <ShieldCheck size={13} /> {score}% Similarity Match
                </span>
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl p-2 text-gray-400 transition hover:bg-gray-800 hover:text-white"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content Preview */}
        <div className="max-h-[55vh] overflow-y-auto p-6 text-sm leading-relaxed text-gray-200">
          <div className="rounded-2xl border border-gray-800/80 bg-[#0d131f] p-4 text-xs font-mono leading-relaxed text-emerald-300/90">
            {content}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between border-t border-gray-800 px-6 py-4 bg-gray-950/60">
          <span className="text-xs text-gray-500">Source grounded in vector database</span>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 rounded-xl border border-gray-800 bg-gray-900 px-4 py-2 text-xs font-semibold text-gray-300 hover:bg-gray-800 hover:text-white"
            >
              {copied ? (
                <>
                  <Check size={14} className="text-emerald-400" />
                  <span className="text-emerald-400">Copied Chunk</span>
                </>
              ) : (
                <>
                  <Copy size={14} />
                  <span>Copy Text Chunk</span>
                </>
              )}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl bg-emerald-500 px-4 py-2 text-xs font-semibold text-gray-950 hover:bg-emerald-400"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
