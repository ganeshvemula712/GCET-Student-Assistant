import { CheckCircle2, LoaderCircle } from "lucide-react";

export default function StatusTimeline({ currentStep = 1 }) {
  const steps = [
    "Uploading PDF",
    "Extracting Text",
    "Chunking Pass",
    "Generating Embeddings",
    "Saving to ChromaDB",
    "Ready",
  ];

  return (
    <div className="mt-4 space-y-2">
      <div className="flex items-center justify-between text-xs text-gray-400">
        <span>RAG Pipeline Progress</span>
        <span className="font-semibold text-emerald-400">
          Step {Math.min(currentStep, steps.length)} of {steps.length}
        </span>
      </div>
      <div className="grid grid-cols-6 gap-1">
        {steps.map((step, idx) => {
          const isDone = idx + 1 < currentStep;
          const isCurrent = idx + 1 === currentStep;

          return (
            <div
              key={step}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                isDone
                  ? "bg-emerald-400"
                  : isCurrent
                  ? "bg-cyan-400 animate-pulse"
                  : "bg-gray-800"
              }`}
              title={step}
            />
          );
        })}
      </div>
      <div className="flex items-center gap-2 text-xs font-semibold text-gray-200 pt-1">
        {currentStep < steps.length ? (
          <LoaderCircle size={14} className="animate-spin text-cyan-400" />
        ) : (
          <CheckCircle2 size={14} className="text-emerald-400" />
        )}
        <span>{steps[Math.min(currentStep - 1, steps.length - 1)]}</span>
      </div>
    </div>
  );
}
