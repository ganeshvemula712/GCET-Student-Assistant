import { useState, useRef, useEffect, memo } from "react";
import { MessageSquare, Pin, Check, LoaderCircle } from "lucide-react";
import ConversationMenu from "./ConversationMenu";

function HighlightText({ text = "", searchQuery = "" }) {
  if (!searchQuery || !searchQuery.trim()) {
    return <span>{text}</span>;
  }
  const parts = text.split(new RegExp(`(${searchQuery.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi"));
  return (
    <span>
      {parts.map((part, i) =>
        part.toLowerCase() === searchQuery.toLowerCase() ? (
          <mark key={i} className="rounded bg-emerald-500/30 px-0.5 font-bold text-emerald-300">
            {part}
          </mark>
        ) : (
          part
        )
      )}
    </span>
  );
}

function formatRelativeTime(dateStr) {
  if (!dateStr) return "Recent";
  const date = new Date(dateStr);
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);

  if (diffInSeconds < 60) return "Just now";
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 172800) return "Yesterday";
  return date.toLocaleDateString([], { month: "short", day: "numeric" });
}

function ConversationItem({
  conversation,
  selected,
  isPinned,
  isArchived,
  searchQuery,
  onSelect,
  onRenameSubmit,
  onPinToggle,
  onArchiveToggle,
  onDuplicate,
  onExport,
  onDeleteRequest,
}) {
  const [editing, setEditing] = useState(false);
  const [titleValue, setTitleValue] = useState(conversation.title || "");
  const [saving, setSaving] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    setTitleValue(conversation.title || "");
  }, [conversation.title]);

  useEffect(() => {
    if (editing) {
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [editing]);

  async function handleSave() {
    const trimmed = titleValue.trim();
    if (!trimmed || trimmed === conversation.title) {
      setEditing(false);
      setTitleValue(conversation.title || "");
      return;
    }

    setSaving(true);
    try {
      await onRenameSubmit?.(conversation.conversation_id, trimmed);
    } finally {
      setSaving(false);
      setEditing(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSave();
    } else if (e.key === "Escape") {
      e.preventDefault();
      setTitleValue(conversation.title || "");
      setEditing(false);
    }
  }

  return (
    <div
      onClick={() => !editing && onSelect(conversation.conversation_id)}
      className={`group relative mb-1.5 flex w-full cursor-pointer items-center justify-between rounded-xl border p-2.5 transition-all duration-200 ${
        selected
          ? "border-emerald-500/40 bg-emerald-500/10 shadow-md shadow-emerald-500/5 text-white"
          : "border-transparent text-gray-300 hover:border-gray-800 hover:bg-[#111827] hover:text-white"
      }`}
    >
      <div className="flex min-w-0 items-center gap-2.5 flex-1 pr-2">
        <div
          className={`flex size-7 shrink-0 items-center justify-center rounded-lg ${
            selected ? "bg-emerald-500 text-gray-950" : "bg-gray-800/80 text-gray-400 group-hover:text-emerald-400"
          }`}
        >
          <MessageSquare size={14} />
        </div>

        <div className="min-w-0 flex-1">
          {editing ? (
            <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
              <input
                ref={inputRef}
                type="text"
                value={titleValue}
                onChange={(e) => setTitleValue(e.target.value)}
                onKeyDown={handleKeyDown}
                onBlur={handleSave}
                disabled={saving}
                className="w-full rounded-md border border-emerald-500/40 bg-gray-900 px-2 py-0.5 text-xs text-white outline-none focus:ring-1 focus:ring-emerald-400"
              />
              {saving ? (
                <LoaderCircle size={14} className="animate-spin text-emerald-400" />
              ) : (
                <button type="button" onClick={handleSave} className="text-emerald-400 hover:text-emerald-300">
                  <Check size={14} />
                </button>
              )}
            </div>
          ) : (
            <>
              <div className="flex items-center gap-1.5">
                <p className="truncate text-xs font-semibold">
                  <HighlightText text={conversation.title || "Untitled Chat"} searchQuery={searchQuery} />
                </p>
                {isPinned && <Pin size={11} className="shrink-0 text-amber-400 fill-amber-400" />}
              </div>
              <div className="mt-0.5 flex items-center justify-between text-[10px] text-gray-500">
                <span className="truncate max-w-[110px]">
                  {conversation.message_count ? `${conversation.message_count} messages` : "Chat session"}
                </span>
                <span>{formatRelativeTime(conversation.created_at)}</span>
              </div>
            </>
          )}
        </div>
      </div>

      {!editing && (
        <ConversationMenu
          conversation={conversation}
          isPinned={isPinned}
          isArchived={isArchived}
          onRename={() => setEditing(true)}
          onPinToggle={onPinToggle}
          onArchiveToggle={onArchiveToggle}
          onDuplicate={onDuplicate}
          onExport={onExport}
          onDelete={() => onDeleteRequest?.(conversation)}
        />
      )}
    </div>
  );
}

export default memo(ConversationItem);