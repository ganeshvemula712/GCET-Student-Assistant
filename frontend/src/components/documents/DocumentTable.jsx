import { useState, useMemo } from "react";
import { Search, Filter, ArrowUpDown, LayoutGrid, List, FileText, Trash2, Eye, CheckCircle2, AlertTriangle } from "lucide-react";
import DocumentCard from "./DocumentCard";

export default function DocumentTable({ documents = [], onInspect, onDelete }) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const [viewMode, setViewMode] = useState("table"); // Default 'table' view

  const filteredDocuments = useMemo(() => {
    return documents
      .filter((doc) => {
        const matchesSearch = !search.trim() || doc.filename?.toLowerCase().includes(search.toLowerCase());
        const matchesStatus =
          statusFilter === "all" ||
          (statusFilter === "active" && doc.is_active !== false) ||
          (statusFilter === "superseded" && doc.is_active === false);

        return matchesSearch && matchesStatus;
      })
      .sort((a, b) => {
        if (sortBy === "newest") {
          return new Date(b.uploaded_at || 0) - new Date(a.uploaded_at || 0);
        }
        if (sortBy === "oldest") {
          return new Date(a.uploaded_at || 0) - new Date(b.uploaded_at || 0);
        }
        if (sortBy === "version") {
          return (b.version || 1) - (a.version || 1);
        }
        return 0;
      });
  }, [documents, search, statusFilter, sortBy]);

  return (
    <div className="space-y-4">
      {/* Search & Filter Bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3.5 top-3 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search documents by filename..."
            className="w-full rounded-2xl border border-gray-800 bg-[#111827] py-2.5 pl-10 pr-4 text-xs text-white placeholder-gray-500 outline-none transition focus:border-emerald-500/40"
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Status Filter */}
          <div className="flex items-center gap-1.5 rounded-2xl border border-gray-800 bg-[#111827] px-3 py-2 text-xs text-gray-300">
            <Filter size={14} className="text-gray-400 shrink-0" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-transparent font-semibold outline-none cursor-pointer"
            >
              <option value="all" className="bg-gray-900">All Versions</option>
              <option value="active" className="bg-gray-900">Active RAG</option>
              <option value="superseded" className="bg-gray-900">Superseded</option>
            </select>
          </div>

          {/* Sort By */}
          <div className="flex items-center gap-1.5 rounded-2xl border border-gray-800 bg-[#111827] px-3 py-2 text-xs text-gray-300">
            <ArrowUpDown size={14} className="text-gray-400 shrink-0" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-transparent font-semibold outline-none cursor-pointer"
            >
              <option value="newest" className="bg-gray-900">Newest First</option>
              <option value="oldest" className="bg-gray-900">Oldest First</option>
              <option value="version" className="bg-gray-900">Latest Version</option>
            </select>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center rounded-2xl border border-gray-800 bg-[#111827] p-1 text-gray-400">
            <button
              type="button"
              onClick={() => setViewMode("table")}
              className={`rounded-xl p-1.5 transition ${viewMode === "table" ? "bg-emerald-500/20 text-emerald-400" : "hover:text-white"}`}
              title="Table View"
            >
              <List size={16} />
            </button>
            <button
              type="button"
              onClick={() => setViewMode("grid")}
              className={`rounded-xl p-1.5 transition ${viewMode === "grid" ? "bg-emerald-500/20 text-emerald-400" : "hover:text-white"}`}
              title="Grid View"
            >
              <LayoutGrid size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Empty Filter State */}
      {filteredDocuments.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-3xl border border-gray-800 bg-[#111827] p-10 text-center">
          <FileText size={32} className="text-gray-600 mb-2" />
          <h3 className="text-sm font-bold text-white">No documents found</h3>
          <p className="mt-1 text-xs text-gray-400">No uploaded files matched your search filters.</p>
        </div>
      ) : viewMode === "grid" ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredDocuments.map((doc) => (
            <DocumentCard
              key={doc.document_id}
              document={doc}
              onInspect={onInspect}
              onDelete={onDelete}
            />
          ))}
        </div>
      ) : (
        <div className="overflow-x-auto rounded-3xl border border-gray-800 bg-[#111827]">
          <table className="w-full text-left text-xs text-gray-300">
            <thead className="border-b border-gray-800 bg-gray-900/60 font-bold uppercase tracking-wider text-gray-400">
              <tr>
                <th className="p-4 align-middle">Filename</th>
                <th className="p-4 align-middle">Category</th>
                <th className="p-4 align-middle w-48 max-w-[190px]">Tags</th>
                <th className="p-4 align-middle">Type</th>
                <th className="p-4 align-middle">Version</th>
                <th className="p-4 align-middle">Pages</th>
                <th className="p-4 align-middle">Vector Chunks</th>
                <th className="p-4 align-middle">RAG Status</th>
                <th className="p-4 align-middle">Uploaded</th>
                <th className="p-4 align-middle text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {filteredDocuments.map((doc) => {
                const ext = doc.filename?.split(".").pop()?.toUpperCase() || "PDF";
                const catName = doc.category || "General Academic";
                const tagList = doc.tags ? doc.tags.split(",").map((t) => t.strip ? t.strip() : t.trim()).filter(Boolean) : [];
                const visibleTags = tagList.slice(0, 2);
                const extraTagCount = tagList.length - visibleTags.length;

                return (
                <tr key={doc.document_id} className="transition hover:bg-gray-800/40">
                  <td className="p-4 align-middle font-bold text-white">
                    <div className="flex items-center gap-2">
                      <FileText size={16} className="text-indigo-400 shrink-0" />
                      <span className="truncate max-w-xs" title={doc.filename}>{doc.filename}</span>
                    </div>
                  </td>
                  <td className="p-4 align-middle">
                    <span className="rounded-full bg-indigo-500/15 border border-indigo-500/30 px-2.5 py-1 text-[11px] font-bold text-indigo-300 whitespace-nowrap">
                      {catName}
                    </span>
                  </td>
                  <td className="p-4 align-middle">
                    {tagList.length > 0 ? (
                      <div className="flex items-center gap-1.5 max-w-[180px] overflow-hidden" title={tagList.join(", ")}>
                        {visibleTags.map((tag) => (
                          <span key={tag} className="rounded-md bg-cyan-500/10 border border-cyan-500/20 px-1.5 py-0.5 text-[10px] font-medium text-cyan-300 truncate max-w-[85px]" title={tag}>
                            {tag}
                          </span>
                        ))}
                        {extraTagCount > 0 && (
                          <span className="rounded-md bg-gray-800 border border-gray-700 px-1.5 py-0.5 text-[10px] font-semibold text-gray-400 shrink-0 cursor-help" title={`All tags: ${tagList.join(", ")}`}>
                            +{extraTagCount}
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-gray-500 text-[11px]">—</span>
                    )}
                  </td>
                  <td className="p-4 align-middle">
                    <span className="rounded-md bg-gray-800 border border-gray-700 px-2 py-0.5 text-[10px] font-bold text-gray-300">
                      {ext}
                    </span>
                  </td>
                  <td className="p-4 align-middle">
                    <span className="rounded-full bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 text-[11px] font-bold text-indigo-300">
                      v{doc.version || 1}
                    </span>
                  </td>
                  <td className="p-4 align-middle">{doc.page_count ?? 1}</td>
                  <td className="p-4 align-middle">{doc.chunk_count ?? 1}</td>
                  <td className="p-4 align-middle">
                    {doc.is_active !== false && (doc.status === "processed" || !doc.status) ? (
                      <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold">
                        <CheckCircle2 size={14} /> Active RAG
                      </span>
                    ) : doc.status === "indexing_required" ? (
                      <span className="inline-flex items-center gap-1 text-amber-400 font-semibold" title="Indexing required or Gemini OCR quota limit reached">
                        <AlertTriangle size={14} /> Indexing Required
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-amber-400 font-semibold" title="Superseded by newer version">
                        <AlertTriangle size={14} /> Superseded
                      </span>
                    )}
                  </td>
                  <td className="p-4 align-middle text-gray-400">
                    {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : "Recent"}
                  </td>
                  <td className="p-4 align-middle text-right">
                    <div className="inline-flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => onInspect?.(doc)}
                        className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-800 hover:text-white"
                        title="View details"
                      >
                        <Eye size={16} />
                      </button>
                      {onDelete && (
                        <button
                          type="button"
                          onClick={() => onDelete?.(doc)}
                          className="rounded-lg p-1.5 text-gray-400 hover:bg-rose-500/10 hover:text-rose-400"
                          title="Delete document"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ); })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}