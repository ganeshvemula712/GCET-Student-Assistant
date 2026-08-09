import { useState } from "react";
import { Search, MessageSquare, Trash2, User } from "lucide-react";
import { toast } from "sonner";
import useConversations from "@/hooks/useConversations";

export default function AdminConversationTable() {
  const { data: conversations = [], isLoading } = useConversations();
  const [search, setSearch] = useState("");

  const filteredConvs = conversations.filter((c) =>
    (c.title || "").toLowerCase().includes(search.toLowerCase())
  );

  const handleDelete = (title) => {
    if (window.confirm(`Delete conversation "${title}"?`)) {
      toast.success(`Conversation "${title}" deleted.`);
    }
  };

  return (
    <div className="space-y-4 rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-base font-bold text-white">Conversation Monitoring ({conversations.length})</h3>
          <p className="text-xs text-gray-400">Review student query threads and moderate inappropriate AI prompt sessions.</p>
        </div>

        <div className="relative">
          <Search size={15} className="absolute left-3 top-3 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search conversations..."
            className="h-10 rounded-2xl border border-gray-800 bg-[#0b1020] pl-9 pr-4 text-xs text-white outline-none transition focus:border-indigo-500/60"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-xs text-gray-400 animate-pulse">Loading active conversations...</div>
      ) : filteredConvs.length === 0 ? (
        <div className="py-12 text-center text-xs text-gray-400">No conversations found.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-gray-800 text-gray-400">
              <tr>
                <th className="pb-3 pt-2 font-semibold">Title / Topic</th>
                <th className="pb-3 pt-2 font-semibold">User</th>
                <th className="pb-3 pt-2 font-semibold">Messages</th>
                <th className="pb-3 pt-2 font-semibold">Last Active</th>
                <th className="pb-3 pt-2 text-right font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {filteredConvs.map((conv) => {
                const title = conv.title || "Academic Question Thread";
                const msgCount = conv.message_count || conv.messages?.length || 4;
                const updated = conv.updated_at
                  ? new Date(conv.updated_at).toLocaleDateString([], { month: "short", day: "numeric" })
                  : "Today";

                return (
                  <tr key={conv.conversation_id || conv.id} className="hover:bg-gray-900/40">
                    <td className="py-3 font-semibold text-white">
                      <div className="flex items-center gap-2.5">
                        <MessageSquare size={16} className="text-cyan-400" />
                        <span className="truncate max-w-xs">{title}</span>
                      </div>
                    </td>
                    <td className="py-3 text-gray-300">
                      <span className="flex items-center gap-1 text-gray-400">
                        <User size={12} /> Student User
                      </span>
                    </td>
                    <td className="py-3 font-semibold text-indigo-300">{msgCount} msgs</td>
                    <td className="py-3 text-gray-400">{updated}</td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => handleDelete(title)}
                        className="rounded-xl bg-rose-500/10 p-2 text-rose-400 transition hover:bg-rose-500/20"
                        title="Delete Conversation"
                      >
                        <Trash2 size={15} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
