import { ShieldCheck, Zap, Sparkles } from "lucide-react";

export default function ConfidenceBadge({ score = 0, sourcesCount = 0 }) {
  const numScore = Number(score) || 0;
  const numSources = Number(sourcesCount) || 0;
  const isRag = numSources > 0;

  let styles;

  if (isRag) {
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

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${styles.bg} ${styles.text} ${styles.border}`}
      title={isRag ? `AI Retrieval Confidence: ${numScore}%` : "General Knowledge AI Answer"}
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
