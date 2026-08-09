import { MessageSquarePlus, Upload, User, Zap, BarChart3 } from "lucide-react";
import QuickActionCard from "./QuickActionCard";
import SectionHeader from "./SectionHeader";

export default function QuickActions() {
  const actions = [
    {
      title: "Ask AI",
      description: "Start a conversation with GCET AI companion",
      icon: MessageSquarePlus,
      to: "/chat",
      badge: "Instant",
    },
    {
      title: "Upload Document",
      description: "Add PDFs to your AI Knowledge Base",
      icon: Upload,
      to: "/documents",
      badge: "RAG",
    },
    {
      title: "User Profile",
      description: "View and update account information",
      icon: User,
      to: "/profile",
    },
    {
      title: "Analytics",
      description: "Inspect usage stats and history",
      icon: BarChart3,
      to: "/dashboard",
    },
  ];

  return (
    <div className="space-y-4">
      <SectionHeader
        title="Quick Actions"
        subtitle="Frequently used tools & workflows"
        icon={Zap}
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {actions.map((action, i) => (
          <QuickActionCard key={action.title} {...action} index={i} />
        ))}
      </div>
    </div>
  );
}