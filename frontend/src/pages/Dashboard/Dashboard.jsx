import DashboardHeader from "@/components/dashboard/DashboardHeader";
import StatCard from "@/components/dashboard/StatCard";
import DashboardSkeleton from "@/components/dashboard/DashboardSkeleton";
import QuickActions from "@/components/dashboard/QuickActions";
import KnowledgeSummary from "@/components/dashboard/KnowledgeSummary";
import RecentConversations from "@/components/dashboard/RecentConversations";
import RecentDocuments from "@/components/dashboard/RecentDocuments";
import ActivityTimeline from "@/components/dashboard/ActivityTimeline";

import { useDashboardStats } from "@/hooks/useDashboardStats";
import { useDocuments } from "@/hooks/useDocuments";
import useConversations from "@/hooks/useConversations";

import {
  MessageSquare,
  Bot,
  BookOpen,
  UserCircle,
  AlertCircle,
} from "lucide-react";

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading, isError: statsError } = useDashboardStats();
  const { data: documents = [], isLoading: docsLoading, isError: docsError } = useDocuments();
  const { data: conversations = [], isLoading: convsLoading, isError: convsError } = useConversations();

  const isLoading = statsLoading && docsLoading && convsLoading;
  const hasError = statsError && docsError && convsError;

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (hasError) {
    return (
      <div className="w-full max-w-7xl mx-auto rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 text-center text-sm font-medium text-rose-400">
        <AlertCircle size={24} className="mx-auto mb-2 text-rose-400" />
        Failed to connect to backend dashboard service. Please ensure the server is running.
      </div>
    );
  }

  const conversationCount = (stats?.conversations && stats.conversations > 0) ? stats.conversations : conversations.length;
  const documentCount = (stats?.documents && stats.documents > 0) ? stats.documents : documents.length;
  const responseCount = stats?.responses ?? 0;
  const accountStatus = stats?.account ?? "Active";

  return (
    <div className="w-full max-w-7xl mx-auto space-y-8 pb-10">
      {/* 1. Welcome Section */}
      <DashboardHeader />

      {/* 2. Statistics Cards Grid */}
      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Total Conversations"
          value={conversationCount}
          subtitle="Active chat sessions"
          icon={MessageSquare}
          color="emerald"
          badgeText="Active"
          index={0}
        />
        <StatCard
          title="AI Answers Generated"
          value={responseCount}
          subtitle="Ground responses provided"
          icon={Bot}
          color="cyan"
          badgeText="Live"
          index={1}
        />
        <StatCard
          title="Knowledge Documents"
          value={documentCount}
          subtitle="Indexed course PDFs"
          icon={BookOpen}
          color="purple"
          badgeText="RAG Ready"
          index={2}
        />
        <StatCard
          title="Account Plan"
          value={accountStatus}
          subtitle="GCET Student Workspace"
          icon={UserCircle}
          color="amber"
          badgeText="Verified"
          index={3}
        />
      </div>

      {/* 3. Quick Actions */}
      <QuickActions />

      {/* 4. Middle Grid: Recent Activity & Knowledge Base */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ActivityTimeline
            conversations={conversations}
            documents={documents}
            isLoading={isLoading}
          />
        </div>
        <div>
          <KnowledgeSummary documents={documents} />
        </div>
      </div>

      {/* 5. Bottom Grid: Recent Conversations & Recent Documents */}
      <div className="grid gap-6 xl:grid-cols-2">
        <RecentConversations />
        <RecentDocuments />
      </div>
    </div>
  );
}