import { Activity, Clock } from "lucide-react";
import ActivityItem from "./ActivityItem";
import SectionHeader from "./SectionHeader";
import EmptyState from "./EmptyState";
import SkeletonLoader from "./SkeletonLoader";

export default function ActivityTimeline({
  conversations = [],
  documents = [],
  isLoading = false,
}) {
  if (isLoading) {
    return (
      <div className="rounded-2xl border border-gray-800 bg-[#111827] p-6 shadow-xl">
        <SectionHeader
          title="Recent Activity"
          subtitle="Real-time user & system events"
          icon={Activity}
        />
        <SkeletonLoader type="list" count={4} />
      </div>
    );
  }

  // Combine conversations and documents into activity items sorted by date
  const activityItems = [
    ...conversations.slice(0, 3).map((conv) => ({
      id: `conv-${conv.conversation_id}`,
      type: "chat",
      title: conv.title || "New Conversation",
      subtitle: `Chat session • ${conv.message_count || 1} messages`,
      date: new Date(conv.created_at || Date.now()),
      status: "Active",
    })),
    ...documents.slice(0, 3).map((doc) => ({
      id: `doc-${doc.document_id}`,
      type: "upload",
      title: doc.filename,
      subtitle: `${doc.page_count || 1} pages • ${doc.chunk_count || 0} chunks processed`,
      date: new Date(doc.upload_date || Date.now()),
      status: "Processed",
    })),
  ].sort((a, b) => b.date - a.date);

  return (
    <div className="rounded-2xl border border-gray-800 bg-[#111827] p-6 shadow-xl">
      <SectionHeader
        title="Recent Activity"
        subtitle="Real-time user & system logs"
        icon={Activity}
      />
      {activityItems.length === 0 ? (
        <EmptyState
          title="No recent activity"
          description="Your activity log will populate as you chat with AI and upload documents."
          icon={Clock}
        />
      ) : (
        <div className="space-y-3">
          {activityItems.slice(0, 5).map((item) => (
            <ActivityItem
              key={item.id}
              type={item.type}
              title={item.title}
              subtitle={item.subtitle}
              time={item.date.toLocaleDateString(undefined, {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
              status={item.status}
            />
          ))}
        </div>
      )}
    </div>
  );
}
