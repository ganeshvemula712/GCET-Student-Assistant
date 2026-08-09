import { useState } from "react";
import { Lock } from "lucide-react";
import AdminHeader from "@/components/admin/AdminHeader";
import AdminStats from "@/components/admin/AdminStats";
import UserTable from "@/components/admin/UserTable";
import AdminDocumentTable from "@/components/admin/AdminDocumentTable";
import AdminConversationTable from "@/components/admin/AdminConversationTable";
import AIAnalyticsCard from "@/components/admin/AIAnalyticsCard";
import SystemHealthCard from "@/components/admin/SystemHealthCard";
import AuditTimeline from "@/components/admin/AuditTimeline";
import AdminSkeleton from "@/components/admin/AdminSkeleton";

import useProfile from "@/hooks/useProfile";
import { useDashboardStats } from "@/hooks/useDashboardStats";

export default function Admin() {
  const [activeTab, setActiveTab] = useState("overview");
  const { data: profile, isLoading: isProfileLoading } = useProfile();
  const { data: dashboardStats } = useDashboardStats();

  if (isProfileLoading) {
    return <AdminSkeleton />;
  }

  const isAdmin = profile?.role === "admin";

  if (!isAdmin) {
    return (
      <div className="mx-auto max-w-2xl py-16 text-center">
        <div className="mx-auto mb-4 flex size-16 items-center justify-center rounded-3xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
          <Lock size={32} />
        </div>
        <h2 className="text-2xl font-extrabold text-white">Administrator Access Required</h2>
        <p className="mt-2 text-xs text-gray-400">
          You do not have administrator permissions to view system metrics, user roles, or Audit logs.
        </p>
      </div>
    );
  }

  const stats = {
    totalUsers: 142,
    totalConversations: dashboardStats?.totalConversations ?? 389,
    uploadedDocuments: dashboardStats?.totalDocuments ?? 48,
    vectorChunks: dashboardStats?.knowledgeBaseDocs ? `${dashboardStats.knowledgeBaseDocs * 24}` : "3,840",
    aiRequests: dashboardStats?.questionsAsked ?? 215,
  };

  return (
    <div className="mx-auto max-w-6xl space-y-8 pb-12">
      <AdminHeader activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === "overview" && (
        <div className="space-y-8">
          <AdminStats stats={stats} />
          <UserTable />
          <div className="grid gap-8 lg:grid-cols-2">
            <SystemHealthCard />
            <AuditTimeline />
          </div>
        </div>
      )}

      {activeTab === "users" && <UserTable />}
      {activeTab === "documents" && <AdminDocumentTable />}
      {activeTab === "conversations" && <AdminConversationTable />}
      {activeTab === "analytics" && <AIAnalyticsCard />}
      {activeTab === "health" && <SystemHealthCard />}
      {activeTab === "audit" && <AuditTimeline />}
    </div>
  );
}
