import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, Trash2, X, LoaderCircle } from "lucide-react";

export default function DeleteDocumentModal({
  open,
  filename = "this document",
  loading = false,
  onConfirm,
  onCancel,
}) {
  if (!open) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onCancel}
          className="absolute inset-0 bg-black/75 backdrop-blur-sm"
        />

        {/* Modal Window */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="relative w-full max-w-md overflow-hidden rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-2xl"
        >
          <button
            type="button"
            onClick={onCancel}
            className="absolute right-4 top-4 rounded-xl p-2 text-gray-400 hover:bg-gray-800 hover:text-white"
          >
            <X size={18} />
          </button>

          <div className="flex size-12 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-400">
            <AlertTriangle size={24} />
          </div>

          <h3 className="mt-4 text-xl font-bold text-white">Delete Document?</h3>
          <p className="mt-2 text-xs leading-relaxed text-gray-400">
            Are you sure you want to delete <strong className="text-white">"{filename}"</strong>? This will permanently remove the PDF document and its vector embeddings from ChromaDB. RAG assistant responses will no longer reference this file.
          </p>

          <div className="mt-6 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onCancel}
              disabled={loading}
              className="rounded-xl border border-gray-800 bg-gray-900 px-4 py-2.5 text-xs font-semibold text-gray-300 transition hover:bg-gray-800 hover:text-white disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={onConfirm}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-xl bg-rose-600 px-4 py-2.5 text-xs font-semibold text-white shadow-lg shadow-rose-600/20 transition hover:bg-rose-500 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <LoaderCircle size={14} className="animate-spin" />
                  <span>Deleting...</span>
                </>
              ) : (
                <>
                  <Trash2 size={14} />
                  <span>Delete Permanently</span>
                </>
              )}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
