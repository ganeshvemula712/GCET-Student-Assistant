import { useState, useRef, useEffect } from "react";
import { UploadCloud, AlertCircle, LoaderCircle, X, RefreshCw, Tag, Folder } from "lucide-react";
import { toast } from "sonner";
import { formatErrorMessage } from "@/utils/error";
import StatusTimeline from "./StatusTimeline";

const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20 MB

const CATEGORY_OPTIONS = [
  "Academic Regulations",
  "Course Syllabus",
  "Placements",
  "Timetables",
  "Examinations",
  "Attendance",
  "Notices & Circulars",
  "General Academic",
];

export default function UploadDropzone({ uploadMutation, existingDocuments = [] }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [currentFile, setCurrentFile] = useState(null);
  const [pipelineStep, setPipelineStep] = useState(1);
  const [errorMsg, setErrorMsg] = useState("");
  const [updateMode, setUpdateMode] = useState(false);
  const [selectedSupersedesId, setSelectedSupersedesId] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("General Academic");
  const [inputTags, setInputTags] = useState("");
  const inputRef = useRef(null);

  // Simulate pipeline step advancement during upload mutation
  useEffect(() => {
    if (!uploadMutation.isPending) {
      if (uploadMutation.isSuccess) {
        setPipelineStep(6);
      }
      return;
    }

    setPipelineStep(1);
    const interval = setInterval(() => {
      setPipelineStep((prev) => (prev < 5 ? prev + 1 : 5));
    }, 1200);

    return () => clearInterval(interval);
  }, [uploadMutation.isPending, uploadMutation.isSuccess]);

  function validateFile(file) {
    setErrorMsg("");
    if (!file) return false;

    const filenameLower = file.name.toLowerCase();
    const validExts = [".pdf", ".docx", ".doc", ".jpg", ".jpeg", ".png"];
    if (!validExts.some((ext) => filenameLower.endsWith(ext))) {
      const err = "Invalid file type. Supported formats: PDF, DOCX, DOC, JPG, JPEG, PNG.";
      setErrorMsg(err);
      toast.error(err);
      return false;
    }

    if (file.size > MAX_FILE_SIZE) {
      const err = "File exceeds 20MB limit. Please upload a smaller PDF document.";
      setErrorMsg(err);
      toast.error(err);
      return false;
    }

    return true;
  }

  function handleFileSelect(file) {
    if (!validateFile(file)) return;

    setCurrentFile(file);
    const supersedesId = updateMode && selectedSupersedesId ? selectedSupersedesId : null;

    uploadMutation.mutate(
      { file, supersedesId, category: selectedCategory, tags: inputTags },
      {
        onSuccess: (data) => {
          toast.success(data?.message || `"${file.name}" uploaded and indexed successfully into ChromaDB!`);
          setTimeout(() => {
            setCurrentFile(null);
            setPipelineStep(1);
            setUpdateMode(false);
            setSelectedSupersedesId("");
            setInputTags("");
          }, 3000);
        },
        onError: (err) => {
          const msg = formatErrorMessage(err, "Failed to upload document.");
          setErrorMsg(msg);
          toast.error(msg);
        },
      }
    );
  }

  function handleDrop(e) {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelect(file);
  }

  function handleChange(e) {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
    e.target.value = "";
  }

  return (
    <div className="w-full space-y-3">
      {/* Upload Settings: Category, Tags, and Versioning Mode */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 rounded-2xl border border-gray-800 bg-[#0f172a]/90 p-3.5 backdrop-blur-sm">
        {/* Category Selector */}
        <div className="flex flex-col space-y-1">
          <label className="text-[11px] font-bold text-gray-300 flex items-center gap-1.5 uppercase tracking-wider">
            <Folder size={13} className="text-indigo-400" />
            <span>Document Category</span>
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            disabled={uploadMutation.isPending}
            className="h-9 w-full rounded-xl border border-gray-800 bg-gray-900 px-3 text-xs text-white outline-none focus:border-indigo-500/70 focus:ring-1 focus:ring-indigo-500/30"
          >
            {CATEGORY_OPTIONS.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        {/* Tags Input */}
        <div className="flex flex-col space-y-1">
          <label className="text-[11px] font-bold text-gray-300 flex items-center gap-1.5 uppercase tracking-wider">
            <Tag size={13} className="text-cyan-400" />
            <span>Optional Indexing Tags</span>
          </label>
          <input
            type="text"
            placeholder="e.g. JNTUH, R22, CSE, Regulations"
            value={inputTags}
            onChange={(e) => setInputTags(e.target.value)}
            disabled={uploadMutation.isPending}
            className="h-9 w-full rounded-xl border border-gray-800 bg-gray-900 px-3 text-xs text-white placeholder-gray-500 outline-none focus:border-cyan-500/70 focus:ring-1 focus:ring-cyan-500/30"
          />
        </div>

        {/* Update Mode / Versioning toggle */}
        {existingDocuments.length > 0 && !uploadMutation.isPending && (
          <div className="md:col-span-2 pt-1.5 flex flex-wrap items-center justify-between gap-3 border-t border-gray-800/60 text-xs text-gray-300">
            <div className="flex items-center gap-2">
              <RefreshCw size={14} className="text-amber-400" />
              <span className="font-semibold text-white">Upload Mode:</span>
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="radio"
                  name="upload_mode"
                  checked={!updateMode}
                  onChange={() => { setUpdateMode(false); setSelectedSupersedesId(""); }}
                  className="text-indigo-500 focus:ring-0"
                />
                <span>New Document</span>
              </label>
              <span className="text-gray-600">•</span>
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="radio"
                  name="upload_mode"
                  checked={updateMode}
                  onChange={() => setUpdateMode(true)}
                  className="text-indigo-500 focus:ring-0"
                />
                <span className="text-amber-300 font-medium">Update Existing Document (Version bump)</span>
              </label>
            </div>

            {updateMode && (
              <select
                value={selectedSupersedesId}
                onChange={(e) => setSelectedSupersedesId(e.target.value)}
                className="h-8 rounded-xl border border-amber-500/30 bg-gray-900 px-3 text-xs text-amber-200 outline-none focus:border-amber-400"
              >
                <option value="">Select document to replace...</option>
                {existingDocuments.map((doc) => (
                  <option key={doc.document_id} value={doc.document_id}>
                    {doc.filename} (v{doc.version || 1})
                  </option>
                ))}
              </select>
            )}
          </div>
        )}
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !uploadMutation.isPending && inputRef.current?.click()}
        className={`group relative flex cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed p-7 text-center transition-all duration-300 ${
          isDragOver
            ? "border-indigo-500 bg-indigo-500/10 shadow-2xl scale-[1.01]"
            : "border-gray-800 bg-[#111827] hover:border-indigo-500/40 hover:bg-[#151e30]"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
          hidden
          onChange={handleChange}
          disabled={uploadMutation.isPending}
        />

        {uploadMutation.isPending ? (
          <div className="w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <LoaderCircle size={44} className="mx-auto mb-3 animate-spin text-indigo-400" />
            <h3 className="text-base font-bold text-white">Indexing "{currentFile?.name}"</h3>
            <p className="mt-1 text-xs text-indigo-300 font-semibold">Categorized as "{selectedCategory}"</p>
            <p className="mt-0.5 text-xs text-gray-400">Processing document chunking and vector embeddings...</p>
            <StatusTimeline currentStep={pipelineStep} />
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className="mb-3 flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 text-indigo-400 border border-indigo-500/30 group-hover:scale-110 transition-transform">
              <UploadCloud size={28} />
            </div>
            <h3 className="text-base font-bold text-white group-hover:text-indigo-400 transition-colors">
              {updateMode ? "Upload Updated Document Version" : "Upload Knowledge Base Document"}
            </h3>
            <p className="mt-1 text-xs text-gray-400 max-w-sm">
              Drag and drop your PDF, Word syllabus, or timetable image here, or click to browse files.
            </p>
            <div className="mt-3 flex items-center gap-3 text-[11px] font-medium text-gray-500">
              <span className="rounded-full bg-gray-900 border border-gray-800 px-3 py-0.5">PDF, DOCX, DOC, JPG, PNG</span>
              <span>•</span>
              <span>Max 20MB</span>
            </div>
          </div>
        )}
      </div>

      {errorMsg && (
        <div className="mt-3 flex items-center justify-between rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">
          <div className="flex items-center gap-2">
            <AlertCircle size={16} className="text-rose-400 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button type="button" onClick={() => setErrorMsg("")} className="text-rose-400 hover:text-white">
            <X size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
