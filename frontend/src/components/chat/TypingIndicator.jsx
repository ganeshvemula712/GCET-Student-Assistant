import { useState, useEffect } from "react";
import { GraduationCap, Database, Sparkles, LoaderCircle } from "lucide-react";

export default function TypingIndicator() {
  const [stepIndex, setStepIndex] = useState(0);

  const steps = [
    { label: "Analyzing prompt & intent...", icon: Sparkles },
    { label: "Searching GCET vector knowledge base...", icon: Database },
    { label: "Synthesizing RAG response...", icon: GraduationCap },
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setStepIndex((prev) => (prev + 1) % steps.length);
    }, 1800);
    return () => clearInterval(timer);
  }, [steps.length]);

  const CurrentIcon = steps[stepIndex].icon;

  return (
    <div className="mb-6 flex justify-start">
      <div className="w-full max-w-3xl">
        <div className="mb-2 flex items-center gap-2.5">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-500 text-gray-950 shadow-md">
            <GraduationCap size={20} />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white">GCET AI Assistant</h4>
            <p className="text-[10px] text-emerald-400">Processing Knowledge Retrieval</p>
          </div>
        </div>

        <div className="rounded-3xl border border-gray-800 bg-[#111827] p-5 shadow-xl">
          <div className="flex items-center gap-3 text-xs text-gray-300">
            <LoaderCircle size={16} className="animate-spin text-emerald-400" />
            <CurrentIcon size={15} className="text-cyan-400" />
            <span className="font-medium text-gray-200">{steps[stepIndex].label}</span>
          </div>
          <div className="mt-3 flex items-center gap-1.5 pl-7">
            <span className="size-2 animate-pulse rounded-full bg-emerald-400" />
            <span className="size-2 animate-pulse rounded-full bg-cyan-400 [animation-delay:200ms]" />
            <span className="size-2 animate-pulse rounded-full bg-purple-400 [animation-delay:400ms]" />
          </div>
        </div>
      </div>
    </div>
  );
}