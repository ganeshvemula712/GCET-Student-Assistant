import { motion, AnimatePresence } from "framer-motion";
import { X, FileText, Layers, Database, Trash2, CheckCircle2, ShieldCheck } from "lucide-react";

export default function DocumentDrawer({ open, document, onClose, onDelete }) {
  if (!open || !document) return null;

  const filename = document.filename || "GCET Document.pdf";
  const pages = document.page_count ?? 1;
  const chunks = document.chunk_count ?? 1;
  const uploadedAt = document.uploaded_at
    ? new Date(document.uploaded_at).toLocaleString([], { dateStyle: "medium", timeStyle: "short" })
    : "Recently";

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        />

        {/* Drawer Window */}
        <motion.div
          initial={{ x: "100%" }}
          animate={{ x: 0 }}
          exit={{ x: "100%" }}
          transition={{ type: "spring", damping: 25, stiffness: 200 }}
          className="relative z-10 flex h-full w-full max-w-md flex-col border-l border-gray-800 bg-[#111827] shadow-2xl"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-800 p-6">
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400">
                <FileText size={20} />
              </div>
              <div className="min-w-0 pr-2">
                <h3 className="truncate text-base font-bold text-white">{filename}</h3>
                <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-400">
                  <CheckCircle2 size={12} /> Ready for RAG Retrieval
                </span>
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl p-2 text-gray-400 hover:bg-gray-800 hover:text-white"
            >
              <X size={18} />
            </button>
          </div>

          {/* Details Body */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Metadata Cards */}
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-2xl border border-gray-800/80 bg-gray-900/60 p-4">
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <Layers size={14} className="text-cyan-400" />
                  <span>Total Pages</span>
                </div>
                <p className="mt-2 text-xl font-extrabold text-white">{pages}</p>
              </div>

              <div className="rounded-2xl border border-gray-800/80 bg-gray-900/60 p-4">
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <Database size={14} className="text-purple-400" />
                  <span>Vector Chunks</span>
                </div>
                <p className="mt-2 text-xl font-extrabold text-white">{chunks}</p>
              </div>
            </div>

            {/* Status & Indexing */}
            <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">Vector Indexing:</span>
                <span className="font-semibold text-emerald-400 inline-flex items-center gap-1">
                  <ShieldCheck size={14} /> Active in ChromaDB
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">Uploaded Date:</span>
                <span className="text-gray-200">{uploadedAt}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">Pipeline Status:</span>
                <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/20">
                  Complete
                </span>
              </div>
            </div>

            {/* Category & Tags Section */}
            <div className="rounded-2xl border border-indigo-500/20 bg-indigo-500/5 p-4 space-y-2.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">Category:</span>
                <span className="rounded-full bg-indigo-500/15 border border-indigo-500/30 px-2.5 py-0.5 text-xs font-bold text-indigo-300">
                  {document.category || "General Academic"}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">Indexing Tags:</span>
                {document.tags ? (
                  <div className="flex flex-wrap gap-1 justify-end max-w-[200px]">
                    {document.tags.split(",").map((t) => t.trim()).filter(Boolean).map((tag) => (
                      <span key={tag} className="rounded-md bg-cyan-500/10 border border-cyan-500/20 px-1.5 py-0.5 text-[10px] font-medium text-cyan-300">
                        {tag}
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-gray-500">—</span>
                )}
              </div>
            </div>

            {/* Chunks Overview */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">
                Knowledge Base Chunks Summary
              </h4>
              <p className="text-xs leading-relaxed text-gray-300 rounded-2xl border border-gray-800 bg-gray-950 p-4">
                This document has been partitioned into {chunks} text chunk(s) stored as vector embeddings for high-precision semantic search query matching during student chat sessions.
              </p>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-between border-t border-gray-800 p-6 bg-gray-950/60">
            <button
              type="button"
              onClick={() => {
                onClose();
                onDelete?.(document);
              }}
              className="inline-flex items-center gap-1.5 rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-2.5 text-xs font-semibold text-rose-400 hover:bg-rose-500/20"
            >
              <Trash2 size={14} />
              <span>Delete Document</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-gray-800 bg-gray-900 px-5 py-2.5 text-xs font-semibold text-white hover:bg-gray-800"
            >
              Close
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
