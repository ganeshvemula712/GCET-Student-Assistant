import { useEffect, useState, useMemo, useCallback } from "react";
import { Plus, MessageSquare, Archive, Sparkles, ChevronDown, ChevronRight } from "lucide-react";
import { toast } from "sonner";

import useConversations from "@/hooks/useConversations";
import useDeleteConversation from "@/hooks/useDeleteConversation";
import useRenameConversation from "@/hooks/useRenameConversation";
import useSearchConversation from "@/hooks/useSearchConversation";

import SearchBar from "./SearchBar";
import ConversationItem from "./ConversationItem";
import DeleteConversationModal from "./DeleteConversationModal";
import SidebarSkeleton from "./SidebarSkeleton";

export default function ChatSidebar({
  selectedConversation,
  onSelectConversation,
  style,
}) {
  const [search, setSearch] = useState("");
  const [pinnedIds, setPinnedIds] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("gcet_pinned_chats") || "[]");
    } catch {
      return [];
    }
  });
  const [archivedIds, setArchivedIds] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("gcet_archived_chats") || "[]");
    } catch {
      return [];
    }
  });
  const [showArchived, setShowArchived] = useState(false);
  const [deleteModalTarget, setDeleteModalTarget] = useState(null);
  const [initialAutoSelectDone, setInitialAutoSelectDone] = useState(false);

  const { data: conversations = [], isLoading, refetch } = useConversations();
  const { data: searchResults = [] } = useSearchConversation(search);

  const renameMutation = useRenameConversation();
  const deleteMutation = useDeleteConversation();

  // Actions
  const handleCreate = useCallback(() => {
    onSelectConversation("new");
    toast.success("New chat session started.");
  }, [onSelectConversation]);

  const handleRenameSubmit = useCallback(
    async (id, newTitle) => {
      try {
        await renameMutation.mutateAsync({ id, title: newTitle });
        refetch();
        toast.success("Chat renamed.");
      } catch (err) {
        console.error(err);
        toast.error("Failed to rename conversation.");
      }
    },
    [renameMutation, refetch]
  );

  const handlePinToggle = useCallback((conv) => {
    setPinnedIds((prev) =>
      prev.includes(conv.conversation_id)
        ? prev.filter((id) => id !== conv.conversation_id)
        : [...prev, conv.conversation_id]
    );
  }, []);

  const handleArchiveToggle = useCallback((conv) => {
    setArchivedIds((prev) =>
      prev.includes(conv.conversation_id)
        ? prev.filter((id) => id !== conv.conversation_id)
        : [...prev, conv.conversation_id]
    );
    toast.info("Conversation updated.");
  }, []);

  const handleDuplicate = useCallback(() => {
    handleCreate();
  }, [handleCreate]);

  // Save pinned & archived preferences to localStorage
  useEffect(() => {
    localStorage.setItem("gcet_pinned_chats", JSON.stringify(pinnedIds));
  }, [pinnedIds]);

  useEffect(() => {
    localStorage.setItem("gcet_archived_chats", JSON.stringify(archivedIds));
  }, [archivedIds]);

  // Global Keyboard Shortcuts (Ctrl+N for New Chat)
  useEffect(() => {
    function handleGlobalKeyDown(e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "n") {
        e.preventDefault();
        handleCreate();
      }
    }
    window.addEventListener("keydown", handleGlobalKeyDown);
    return () => window.removeEventListener("keydown", handleGlobalKeyDown);
  }, [handleCreate]);

  const rawList = search.trim() === "" ? conversations : searchResults;

  // Filter out archived unless viewing archived
  const activeList = useMemo(() => {
    return rawList.filter((conv) => !archivedIds.includes(conv.conversation_id));
  }, [rawList, archivedIds]);

  const archivedList = useMemo(() => {
    return rawList.filter((conv) => archivedIds.includes(conv.conversation_id));
  }, [rawList, archivedIds]);

  // Group active list by Date
  const groupedConversations = useMemo(() => {
    const pinned = [];
    const today = [];
    const yesterday = [];
    const last7Days = [];
    const last30Days = [];
    const older = [];

    const now = new Date();
    const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const startOfYesterday = new Date(startOfToday.getTime() - 86400000);
    const startOf7Days = new Date(startOfToday.getTime() - 7 * 86400000);
    const startOf30Days = new Date(startOfToday.getTime() - 30 * 86400000);

    activeList.forEach((conv) => {
      if (pinnedIds.includes(conv.conversation_id)) {
        pinned.push(conv);
        return;
      }

      const date = conv.created_at ? new Date(conv.created_at) : new Date();
      if (date >= startOfToday) today.push(conv);
      else if (date >= startOfYesterday) yesterday.push(conv);
      else if (date >= startOf7Days) last7Days.push(conv);
      else if (date >= startOf30Days) last30Days.push(conv);
      else older.push(conv);
    });

    return { pinned, today, yesterday, last7Days, last30Days, older };
  }, [activeList, pinnedIds]);

  // Auto select top conversation ONLY ON INITIAL APP LOAD if no conversation selected
  useEffect(() => {
    if (!initialAutoSelectDone && activeList.length && selectedConversation === null) {
      setInitialAutoSelectDone(true);
      onSelectConversation(activeList[0].conversation_id);
    }
  }, [activeList, selectedConversation, onSelectConversation, initialAutoSelectDone]);

  const handleExport = useCallback((conv) => {
    const text = `# ${conv.title}\n\nExported conversation history from GCET AI Assistant.\nCreated: ${conv.created_at}\n\n`;
    const blob = new Blob([text], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${(conv.title || "chat").replace(/[^a-z0-9]/gi, "_").toLowerCase()}.md`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Exported to Markdown file.");
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    if (!deleteModalTarget) return;
    const targetId = deleteModalTarget.conversation_id;

    try {
      await deleteMutation.mutateAsync(targetId);
      setDeleteModalTarget(null);
      await refetch();
      if (selectedConversation === targetId) {
        onSelectConversation("new");
      }
      toast.success("Conversation deleted.");
    } catch (err) {
      console.error(err);
      toast.error("Unable to delete conversation.");
    }
  }, [deleteModalTarget, deleteMutation, refetch, selectedConversation, onSelectConversation]);

  const renderSection = (title, items) => {
    if (!items || items.length === 0) return null;
    return (
      <div className="mb-4">
        <h4 className="mb-1.5 px-2 text-[10px] font-extrabold uppercase tracking-wider text-gray-400">
          {title} ({items.length})
        </h4>
        {items.map((conv) => (
          <ConversationItem
            key={conv.conversation_id}
            conversation={conv}
            selected={selectedConversation === conv.conversation_id}
            isPinned={pinnedIds.includes(conv.conversation_id)}
            isArchived={archivedIds.includes(conv.conversation_id)}
            searchQuery={search}
            onSelect={onSelectConversation}
            onRenameSubmit={handleRenameSubmit}
            onPinToggle={handlePinToggle}
            onArchiveToggle={handleArchiveToggle}
            onDuplicate={handleDuplicate}
            onExport={handleExport}
            onDeleteRequest={setDeleteModalTarget}
          />
        ))}
      </div>
    );
  };

  return (
    <>
      <aside style={style} className="flex h-full w-70 flex-col border-r border-gray-800/80 bg-[#0B1220] shadow-xl">
        {/* Header CTA & Search */}
        <div className="space-y-3 border-b border-gray-800/80 p-4">
          <button
            type="button"
            onClick={handleCreate}
            className="group flex w-full items-center justify-between rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 px-4 py-3 text-xs font-bold text-gray-950 shadow-lg shadow-emerald-500/20 transition-all duration-200 hover:from-emerald-400 hover:to-teal-400 cursor-pointer"
          >
            <div className="flex items-center gap-2">
              <Plus size={16} />
              <span>New Chat</span>
            </div>
            <span className="rounded bg-black/20 px-1.5 py-0.5 font-mono text-[10px] text-gray-900 font-bold">
              ⌘N
            </span>
          </button>

          <SearchBar value={search} onChange={setSearch} />
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto px-3 py-3">
          {isLoading ? (
            <SidebarSkeleton />
          ) : activeList.length === 0 && search.trim() !== "" ? (
            <div className="flex flex-col items-center justify-center p-6 text-center">
              <MessageSquare size={28} className="text-gray-600 mb-2" />
              <p className="text-xs font-semibold text-gray-300">No matching chats</p>
              <p className="mt-1 text-[11px] text-gray-500">No conversations found for "{search}"</p>
            </div>
          ) : activeList.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-6 text-center">
              <Sparkles size={28} className="text-emerald-500/40 mb-2" />
              <p className="text-xs font-semibold text-gray-300">No conversations yet</p>
              <p className="mt-1 text-[11px] text-gray-500">Start your first AI study session</p>
            </div>
          ) : (
            <>
              {renderSection("Pinned", groupedConversations.pinned)}
              {renderSection("Today", groupedConversations.today)}
              {renderSection("Yesterday", groupedConversations.yesterday)}
              {renderSection("Previous 7 Days", groupedConversations.last7Days)}
              {renderSection("Previous 30 Days", groupedConversations.last30Days)}
              {renderSection("Older", groupedConversations.older)}

              {/* Archived Section Toggle */}
              {archivedList.length > 0 && (
                <div className="mt-4 border-t border-gray-800/60 pt-3">
                  <button
                    type="button"
                    onClick={() => setShowArchived((prev) => !prev)}
                    className="flex w-full items-center justify-between rounded-xl px-2 py-1.5 text-[11px] font-bold uppercase tracking-wider text-gray-400 hover:text-white"
                  >
                    <span className="flex items-center gap-1.5">
                      <Archive size={13} /> Archived Chats ({archivedList.length})
                    </span>
                    {showArchived ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                  </button>
                  {showArchived && renderSection("Archived", archivedList)}
                </div>
              )}
            </>
          )}
        </div>
      </aside>

      {/* Delete Confirmation Modal */}
      <DeleteConversationModal
        open={Boolean(deleteModalTarget)}
        title={deleteModalTarget?.title}
        isDeleting={deleteMutation.isPending}
        onConfirm={handleDeleteConfirm}
        onClose={() => setDeleteModalTarget(null)}
      />
    </>
  );
}