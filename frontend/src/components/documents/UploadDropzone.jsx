import { useState, useRef, useEffect } from "react";
import { UploadCloud, AlertCircle, LoaderCircle, X, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import StatusTimeline from "./StatusTimeline";

const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20 MB

export default function UploadDropzone({ uploadMutation, existingDocuments = [] }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [currentFile, setCurrentFile] = useState(null);
  const [pipelineStep, setPipelineStep] = useState(1);
  const [errorMsg, setErrorMsg] = useState("");
  const [updateMode, setUpdateMode] = useState(false);
  const [selectedSupersedesId, setSelectedSupersedesId] = useState("");
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

    uploadMutation.mutate({ file, supersedesId }, {
      onSuccess: (data) => {
        toast.success(data?.message || `"${file.name}" uploaded and indexed successfully into ChromaDB!`);
        setTimeout(() => {
          setCurrentFile(null);
          setPipelineStep(1);
          setUpdateMode(false);
          setSelectedSupersedesId("");
        }, 3000);
      },
      onError: (err) => {
        const msg = err.response?.data?.detail || "Failed to upload document.";
        setErrorMsg(msg);
        toast.error(msg);
      },
    });
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
      {existingDocuments.length > 0 && !uploadMutation.isPending && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-gray-800 bg-[#0f172a]/80 px-4 py-2 text-xs text-gray-300 backdrop-blur-sm">
          <div className="flex items-center gap-2">
            <RefreshCw size={14} className="text-cyan-400" />
            <span className="font-semibold text-white">Upload Mode:</span>
            <label className="flex items-center gap-1.5 cursor-pointer">
              <input
                type="radio"
                name="upload_mode"
                checked={!updateMode}
                onChange={() => { setUpdateMode(false); setSelectedSupersedesId(""); }}
                className="text-emerald-500 focus:ring-0"
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
                className="text-emerald-500 focus:ring-0"
              />
              <span className="text-amber-300 font-medium">Update Existing Document (Version bump)</span>
            </label>
          </div>

          {updateMode && (
            <select
              value={selectedSupersedesId}
              onChange={(e) => setSelectedSupersedesId(e.target.value)}
              className="rounded-xl border border-amber-500/30 bg-gray-900 px-3 py-1 text-xs text-amber-200 outline-none focus:border-amber-400"
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
            ? "border-emerald-500 bg-emerald-500/10 shadow-2xl scale-[1.01]"
            : "border-gray-800 bg-[#111827] hover:border-emerald-500/40 hover:bg-[#151e30]"
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
            <LoaderCircle size={44} className="mx-auto mb-3 animate-spin text-emerald-400" />
            <h3 className="text-base font-bold text-white">Indexing "{currentFile?.name}"</h3>
            <p className="mt-1 text-xs text-gray-400">Processing document chunking and vector embeddings...</p>
            <StatusTimeline currentStep={pipelineStep} />
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className="mb-3 flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 text-emerald-400 border border-emerald-500/30 group-hover:scale-110 transition-transform">
              <UploadCloud size={28} />
            </div>
            <h3 className="text-base font-bold text-white group-hover:text-emerald-400 transition-colors">
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
