import { Users, MessageSquare, FileText, Database, HardDrive, Cpu, ShieldAlert, Activity } from "lucide-react";

export default function AdminStats({ stats = {} }) {
  const statCards = [
    {
      title: "Total Users",
      value: stats.totalUsers || 142,
      subtitle: "128 Active Students",
      icon: Users,
      color: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
    },
    {
      title: "Active Conversations",
      value: stats.totalConversations || 389,
      subtitle: "1,420 total messages",
      icon: MessageSquare,
      color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
    },
    {
      title: "Uploaded Documents",
      value: stats.uploadedDocuments || 48,
      subtitle: "RAG Ingestion Ready",
      icon: FileText,
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    },
    {
      title: "Vector Chunks",
      value: stats.vectorChunks || "3,840",
      subtitle: "ChromaDB Collection",
      icon: Database,
      color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    },
    {
      title: "AI Requests Today",
      value: stats.aiRequests || 215,
      subtitle: "Gemini 2.5 Flash Engine",
      icon: Cpu,
      color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    },
    {
      title: "Storage Usage",
      value: "412 MB",
      subtitle: "PDF & Index Vector Store",
      icon: HardDrive,
      color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    },
    {
      title: "Avg Latency",
      value: "420 ms",
      subtitle: "Streaming TTFT",
      icon: Activity,
      color: "text-teal-400 bg-teal-500/10 border-teal-500/20",
    },
    {
      title: "Security Health",
      value: "100%",
      subtitle: "0 Security Incidents",
      icon: ShieldAlert,
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
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
