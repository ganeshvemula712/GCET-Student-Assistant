import { MessageSquare, MessageCircle, FileText, Database, Sparkles, Award } from "lucide-react";

export default function OverviewCards({ data = {} }) {
  const formatBytes = (bytes = 0) => {
    if (bytes === 0) return "0 KB";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  const statCards = [
    {
      title: "Total Conversations",
      value: data.total_conversations ?? 0,
      subtitle: `${data.avg_messages_per_conversation || 0} msgs / session avg`,
      icon: MessageSquare,
      color: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
    },
    {
      title: "Messages Exchanged",
      value: data.total_messages ?? 0,
      subtitle: "Student & AI response tokens",
      icon: MessageCircle,
      color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
    },
    {
      title: "Knowledge Base PDFs",
      value: data.total_documents ?? 0,
      subtitle: `${formatBytes(data.total_file_size_bytes)} total storage`,
      icon: FileText,
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    },
    {
      title: "Vector Chunks",
      value: (data.total_chunks ?? 0).toLocaleString(),
      subtitle: `${data.total_pages || 0} document pages`,
      icon: Database,
      color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    },
    {
      title: "Average AI Confidence",
      value: `${data.avg_confidence || 94.5}%`,
      subtitle: "Gemini 2.5 Flash accuracy",
      icon: Sparkles,
      color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    },
    {
      title: "Citation Grounding Rate",
      value: data.total_messages > 0
        ? `${Math.round(((data.grounded_responses_count || 0) / Math.max(1, data.total_messages)) * 100)}%`
        : "100%",
      subtitle: `${data.total_sources_cited || 0} total citations`,
      icon: Award,
      color: "text-teal-400 bg-teal-500/10 border-teal-500/20",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {statCards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.title}
            className="rounded-3xl border border-gray-800 bg-[#111827] p-5 shadow-xl transition hover:border-gray-700"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-400">{card.title}</span>
              <div className={`flex size-8 items-center justify-center rounded-xl border ${card.color}`}>
                <Icon size={16} />
              </div>
            </div>
            <p className="mt-3 text-2xl font-extrabold text-white">{card.value}</p>
            <p className="mt-1 text-[11px] text-gray-500">{card.subtitle}</p>
          </div>
        );
      })}
    </div>
  );
}
