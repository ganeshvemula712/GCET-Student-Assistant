import { FileText, CheckCircle2, FileUp } from "lucide-react";
import { Link } from "react-router-dom";
import { useDocuments } from "@/hooks/useDocuments";
import SectionHeader from "./SectionHeader";
import EmptyState from "./EmptyState";
import SkeletonLoader from "./SkeletonLoader";

export default function RecentDocuments() {
  const { data = [], isLoading } = useDocuments();

  return (
    <div className="rounded-2xl border border-gray-800 bg-[#111827] p-6 shadow-xl">
      <SectionHeader
        title="Knowledge Base Documents"
        subtitle="Uploaded PDFs & study materials"
        icon={FileText}
        actionText="Manage"
        actionPath="/documents"
      />
      {isLoading ? (
        <SkeletonLoader type="list" count={4} />
      ) : data.length === 0 ? (
        <EmptyState
          title="No documents uploaded"
          description="Upload course materials and regulations to power RAG answers."
          actionText="Upload PDF"
          actionPath="/documents"
          icon={FileUp}
        />
      ) : (
        <div className="space-y-3">
          {data.slice(0, 5).map((doc) => (
            <Link
              key={doc.document_id}
              to="/documents"
              className="group flex items-center justify-between rounded-xl border border-gray-800/80 bg-[#111827]/80 p-4 transition-all duration-200 hover:border-cyan-500/30 hover:bg-[#151e30]"
            >
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-white group-hover:text-cyan-400">
                  {doc.filename}
                </p>
                <div className="mt-1 flex items-center gap-3 text-xs text-gray-400">
                  <span>
                    {doc.upload_date
                      ? new Date(doc.upload_date).toLocaleDateString(undefined, {
                          month: "short",
                          day: "numeric",
                        })
                      : "Recently added"}
                  </span>
                  <span>•</span>
                  <span>{doc.page_count || 1} pages</span>
                  <span>•</span>
                  <span>{doc.chunk_count || 0} chunks</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-0.5 text-[11px] font-medium text-emerald-400">
                  <CheckCircle2 size={12} /> Indexed
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}