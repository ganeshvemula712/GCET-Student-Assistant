import { FileText, Database, HardDrive, CheckCircle2, Layers } from "lucide-react";

export default function DocumentStatsCard({ data = {} }) {
  const docsStatus = data.documents_status || {};
  const readyCount = docsStatus.ready ?? data.total_documents ?? 0;

  const formatBytes = (bytes = 0) => {
    if (bytes === 0) return "0 KB";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  return (
    <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl space-y-5">
      <div className="flex items-center justify-between border-b border-gray-800 pb-3">
        <div className="flex items-center gap-2">
          <FileText size={18} className="text-emerald-400" />
          <h3 className="text-base font-bold text-white">Document & Vector Repository</h3>
        </div>
        <span className="rounded-full bg-cyan-500/10 border border-cyan-500/20 px-2.5 py-0.5 text-[10px] font-bold text-cyan-400">
          ChromaDB Vector Store
        </span>
      </div>

      <div className="space-y-3 text-xs">
        <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 size={16} className="text-emerald-400" />
            <span className="text-gray-300">Ready & Indexed PDFs</span>
          </div>
          <span className="font-bold text-white">{readyCount} documents</span>
        </div>

        <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3">
          <div className="flex items-center gap-2.5">
            <Layers size={16} className="text-indigo-400" />
            <span className="text-gray-300">Extracted Vector Chunks</span>
          </div>
          <span className="font-bold text-indigo-300">{(data.total_chunks || 0).toLocaleString()} chunks</span>
        </div>

        <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3">
          <div className="flex items-center gap-2.5">
            <Database size={16} className="text-purple-400" />
            <span className="text-gray-300">Document Page Volume</span>
          </div>
          <span className="font-bold text-purple-300">{(data.total_pages || 0).toLocaleString()} pages</span>
        </div>

        <div className="flex items-center justify-between rounded-2xl border border-gray-800 bg-gray-900/60 p-3">
          <div className="flex items-center gap-2.5">
            <HardDrive size={16} className="text-cyan-400" />
            <span className="text-gray-300">Total PDF Storage Size</span>
          </div>
          <span className="font-bold text-cyan-300">{formatBytes(data.total_file_size_bytes)}</span>
        </div>
      </div>
    </div>
  );
}
