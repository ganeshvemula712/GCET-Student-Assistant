import { MessageSquare, MessageCircle, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import useConversations from "@/hooks/useConversations";
import SectionHeader from "./SectionHeader";
import EmptyState from "./EmptyState";
import SkeletonLoader from "./SkeletonLoader";

export default function RecentConversations() {
  const { data = [], isLoading } = useConversations();

  return (
    <div className="rounded-2xl border border-gray-800 bg-[#111827] p-6 shadow-xl">
      <SectionHeader
        title="Recent Conversations"
        subtitle="Your latest AI sessions"
        icon={MessageSquare}
        actionText="View all"
        actionPath="/chat"
      />
      {isLoading ? (
        <SkeletonLoader type="list" count={4} />
      ) : data.length === 0 ? (
        <EmptyState
          title="No conversations yet"
          description="Start a chat session with your AI assistant."
          actionText="New Chat"
          actionPath="/chat"
          icon={MessageCircle}
        />
      ) : (
        <div className="space-y-3">
          {data.slice(0, 5).map((conv) => (
            <Link
              key={conv.conversation_id}
              to="/chat"
              className="group flex items-center justify-between rounded-xl border border-gray-800/80 bg-[#111827]/80 p-4 transition-all duration-200 hover:border-emerald-500/30 hover:bg-[#151e30]"
            >
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-white group-hover:text-emerald-400">
                  {conv.title || "Untitled Conversation"}
                </p>
                <div className="mt-1 flex items-center gap-3 text-xs text-gray-400">
                  <span>
                    {new Date(conv.created_at || Date.now()).toLocaleDateString(
                      undefined,
                      { month: "short", day: "numeric" }
                    )}
                  </span>
                  <span>•</span>
                  <span>{conv.message_count || 1} messages</span>
                </div>
              </div>
              <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-gray-800/60 text-gray-400 transition-colors duration-200 group-hover:bg-emerald-500/10 group-hover:text-emerald-400">
                <ArrowRight size={16} />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}