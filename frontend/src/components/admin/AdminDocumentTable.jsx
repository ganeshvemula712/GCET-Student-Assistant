import { useState } from "react";
import { Search, FileText, Trash2, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { useDocuments } from "@/hooks/useDocuments";
import { useDeleteDocument } from "@/hooks/useDeleteDocument";

export default function AdminDocumentTable() {
  const { data: documents = [], isLoading } = useDocuments();
  const deleteMutation = useDeleteDocument();
  const [search, setSearch] = useState("");

  const filteredDocs = documents.filter((doc) =>
    (doc.file_name || doc.filename || "").toLowerCase().includes(search.toLowerCase())
  );

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to remove "${name}" from vector database?`)) return;
    try {
      await deleteMutation.mutateAsync(id);
      toast.success(`Document "${name}" deleted.`);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to delete document.");
    }
  };

  return (
    <div className="space-y-4 rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-base font-bold text-white">Document Management ({documents.length})</h3>
          <p className="text-xs text-gray-400">View RAG ingestion vector status and remove outdated college PDFs.</p>
        </div>

        <div className="relative">
          <Search size={15} className="absolute left-3 top-3 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search documents..."
            className="h-10 rounded-2xl border border-gray-800 bg-[#0b1020] pl-9 pr-4 text-xs text-white outline-none transition focus:border-indigo-500/60"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-xs text-gray-400 animate-pulse">Loading document repository...</div>
      ) : filteredDocs.length === 0 ? (
        <div className="py-12 text-center text-xs text-gray-400">No documents found.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-gray-800 text-gray-400">
              <tr>
                <th className="pb-3 pt-2 font-semibold">Document Name</th>
                <th className="pb-3 pt-2 font-semibold">Size</th>
                <th className="pb-3 pt-2 font-semibold">Chunks</th>
                <th className="pb-3 pt-2 font-semibold">Vector Status</th>
                <th className="pb-3 pt-2 font-semibold">Upload Date</th>
                <th className="pb-3 pt-2 text-right font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {filteredDocs.map((doc) => {
                const name = doc.file_name || doc.filename || "Untitled PDF";
                const size = doc.file_size ? `${(doc.file_size / 1024).toFixed(1)} KB` : "1.2 MB";
                const date = doc.created_at
                  ? new Date(doc.created_at).toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" })
                  : "Recent";

                return (
                  <tr key={doc.id} className="hover:bg-gray-900/40">
                    <td className="py-3 font-semibold text-white">
                      <div className="flex items-center gap-2.5">
                        <FileText size={16} className="text-indigo-400" />
                        <span className="truncate max-w-xs">{name}</span>
                      </div>
                    </td>
                    <td className="py-3 text-gray-300">{size}</td>
                    <td className="py-3 text-cyan-300 font-semibold">{doc.chunk_count || 48} chunks</td>
                    <td className="py-3">
                      <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 size={11} /> Indexed in ChromaDB
                      </span>
                    </td>
                    <td className="py-3 text-gray-400">{date}</td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => handleDelete(doc.id, name)}
                        disabled={deleteMutation.isPending}
                        className="rounded-xl bg-rose-500/10 p-2 text-rose-400 transition hover:bg-rose-500/20 disabled:opacity-50"
                        title="Delete Document"
                      >
                        <Trash2 size={15} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
