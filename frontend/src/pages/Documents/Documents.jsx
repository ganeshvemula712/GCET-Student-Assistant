import { useState, useCallback } from "react";
import { ShieldCheck, BookOpen, Layers } from "lucide-react";
import DocumentHeader from "../../components/documents/DocumentHeader";
import UploadDropzone from "../../components/documents/UploadDropzone";
import DocumentTable from "../../components/documents/DocumentTable";
import EmptyDocuments from "../../components/documents/EmptyDocuments";
import DeleteDocumentModal from "../../components/documents/DeleteDocumentModal";
import DocumentDrawer from "../../components/documents/DocumentDrawer";
import DocumentSkeleton from "../../components/documents/DocumentSkeleton";

import { useDocuments } from "../../hooks/useDocuments";
import { useUploadDocument } from "../../hooks/useUploadDocument";
import { useDeleteDocument } from "../../hooks/useDeleteDocument";
import useProfile from "../../hooks/useProfile";

const CATEGORIES = [
  "All",
  "Academic Regulations",
  "Course Syllabus",
  "Placements",
  "Timetables",
  "Examinations",
  "Attendance",
  "Notices & Circulars",
  "General Academic",
];

export default function Documents() {
  const { data: profile } = useProfile();
  const isAdmin = profile?.role === "admin";

  const [activeCategory, setActiveCategory] = useState("All");

  const { data: documents = [], isLoading } = useDocuments({
    enabled: true,
    category: activeCategory !== "All" ? activeCategory : null,
  });

  const uploadMutation = useUploadDocument();
  const deleteMutation = useDeleteDocument();

  const [selectedForDelete, setSelectedForDelete] = useState(null);
  const [inspectDocument, setInspectDocument] = useState(null);

  const handleDeleteRequest = useCallback((doc) => {
    setSelectedForDelete(doc);
  }, []);

  const handleInspectRequest = useCallback((doc) => {
    setInspectDocument(doc);
  }, []);

  const confirmDelete = useCallback(() => {
    if (!selectedForDelete) return;

    deleteMutation.mutate(selectedForDelete.document_id, {
      onSuccess: () => {
        setSelectedForDelete(null);
        if (inspectDocument?.document_id === selectedForDelete.document_id) {
          setInspectDocument(null);
        }
      },
    });
  }, [deleteMutation, selectedForDelete, inspectDocument]);

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      <DocumentHeader documents={documents} />

      {/* Role-based Header Banner */}
      {!isAdmin ? (
        <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-indigo-500/20 bg-[#111827]/90 px-5 py-3.5 shadow-lg backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="flex size-9 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <BookOpen size={18} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">GCET Knowledge Base Catalog</h3>
              <p className="text-xs text-gray-400">
                Official course documents, exam regulations, and syllabus files indexed for AI Assistant grounding.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-indigo-500/20 bg-indigo-500/10 px-3.5 py-1 text-xs font-semibold text-indigo-300">
            <ShieldCheck size={14} className="text-indigo-400" />
            <span>Knowledge Base managed by GCET administrators</span>
          </div>
        </div>
      ) : (
        <UploadDropzone uploadMutation={uploadMutation} existingDocuments={documents} />
      )}

      {/* Category Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-gray-800 bg-[#0f172a]/80 p-2 backdrop-blur-sm overflow-x-auto scrollbar-none">
        <div className="flex items-center gap-1.5 px-2 text-xs font-bold text-gray-400 shrink-0">
          <Layers size={14} className="text-indigo-400" />
          <span>Category Filter:</span>
        </div>
        {CATEGORIES.map((cat) => {
          const isActive = activeCategory === cat;
          return (
            <button
              key={cat}
              type="button"
              onClick={() => setActiveCategory(cat)}
              className={`rounded-xl px-3 py-1.5 text-xs font-bold transition-all duration-150 shrink-0 cursor-pointer ${
                isActive
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30 border border-indigo-400/40"
                  : "bg-gray-900/60 text-gray-400 hover:bg-gray-800 hover:text-white border border-gray-800"
              }`}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <DocumentSkeleton />
      ) : documents.length === 0 ? (
        <EmptyDocuments />
      ) : (
        <DocumentTable
          documents={documents}
          onInspect={handleInspectRequest}
          onDelete={isAdmin ? handleDeleteRequest : undefined}
          isAdmin={isAdmin}
        />
      )}

      {/* Details Side Drawer */}
      <DocumentDrawer
        open={Boolean(inspectDocument)}
        document={inspectDocument}
        onClose={() => setInspectDocument(null)}
        onDelete={isAdmin ? handleDeleteRequest : undefined}
      />

      {/* Delete Confirmation Modal (Admin only) */}
      {isAdmin && (
        <DeleteDocumentModal
          open={Boolean(selectedForDelete)}
          filename={selectedForDelete?.filename}
          loading={deleteMutation.isPending}
          onCancel={() => setSelectedForDelete(null)}
          onConfirm={confirmDelete}
        />
      )}
    </div>
  );
}