import { ShieldCheck, Zap, Sparkles } from "lucide-react";

export default function ConfidenceBadge({ score = 0, sourcesCount = 0, mode = null, content = "" }) {
  const numScore = Number(score) || 0;
  const numSources = Number(sourcesCount) || 0;

  // Determine effective mode: explicit backend mode or fallback logic for legacy message data
  const effectiveMode = mode || (
    numSources > 0
      ? "rag"
      : (content && content.includes("retrieval is temporarily unavailable")
          ? "retrieval_unavailable"
          : "general")
  );

  let styles;

  if (effectiveMode === "retrieval_unavailable") {
    styles = {
      bg: "bg-rose-500/10",
      text: "text-rose-400",
      border: "border-rose-500/20",
      label: "Retrieval Unavailable",
      icon: Zap,
    };
  } else if (effectiveMode === "knowledge_unavailable") {
    styles = {
      bg: "bg-amber-500/10",
      text: "text-amber-400",
      border: "border-amber-500/20",
      label: "Knowledge Base Unavailable",
      icon: Zap,
    };
  } else if (effectiveMode === "rag") {
    if (numScore >= 80) {
      styles = {
        bg: "bg-emerald-500/10",
        text: "text-emerald-400",
        border: "border-emerald-500/20",
        label: "Verified RAG",
        icon: ShieldCheck,
      };
    } else {
      styles = {
        bg: "bg-amber-500/10",
        text: "text-amber-400",
        border: "border-amber-500/20",
        label: "Moderate Context",
        icon: Zap,
      };
    }
  } else {
    styles = {
      bg: "bg-cyan-500/10",
      text: "text-cyan-400",
      border: "border-cyan-500/20",
      label: "General Knowledge",
      icon: Sparkles,
    };
  }

  const Icon = styles.icon;
  const isRag = effectiveMode === "rag";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${styles.bg} ${styles.text} ${styles.border}`}
      title={isRag ? `AI Retrieval Confidence: ${numScore}%` : styles.label}
    >
      <Icon size={13} />
      <span>{styles.label}</span>
      {isRag && numScore > 0 && (
        <span className="ml-1 rounded-md bg-black/30 px-1.5 py-0.5 text-[10px] font-mono font-bold">
          {numScore}%
        </span>
      )}
    </span>
  );
}
