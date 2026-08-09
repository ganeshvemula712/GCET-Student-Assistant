import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { MoreVertical, Edit2, Pin, PinOff, Download, Copy, Archive, RotateCcw, Trash2 } from "lucide-react";

export default function ConversationMenu({
  conversation,
  isPinned,
  isArchived,
  onRename,
  onPinToggle,
  onArchiveToggle,
  onDuplicate,
  onExport,
  onDelete,
}) {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          type="button"
          onClick={(e) => e.stopPropagation()}
          className="flex size-7 items-center justify-center rounded-lg text-gray-400 opacity-0 transition-opacity duration-200 group-hover:opacity-100 hover:bg-gray-800 hover:text-white"
          title="Conversation options"
          aria-label="More options"
        >
          <MoreVertical size={16} />
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="z-50 min-w-[180px] overflow-hidden rounded-2xl border border-gray-800 bg-[#111827] p-1.5 shadow-2xl backdrop-blur-md"
          sideOffset={5}
          align="end"
          onClick={(e) => e.stopPropagation()}
        >
          <DropdownMenu.Item
            className="flex cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-gray-200 outline-none hover:bg-gray-800 hover:text-white"
            onClick={() => onRename?.(conversation)}
          >
            <Edit2 size={14} className="text-cyan-400" />
            <span>Rename</span>
          </DropdownMenu.Item>

          <DropdownMenu.Item
            className="flex cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-gray-200 outline-none hover:bg-gray-800 hover:text-white"
            onClick={() => onPinToggle?.(conversation)}
          >
            {isPinned ? (
              <>
                <PinOff size={14} className="text-amber-400" />
                <span>Unpin</span>
              </>
            ) : (
              <>
                <Pin size={14} className="text-amber-400" />
                <span>Pin to top</span>
              </>
            )}
          </DropdownMenu.Item>

          <DropdownMenu.Item
            className="flex cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-gray-200 outline-none hover:bg-gray-800 hover:text-white"
            onClick={() => onDuplicate?.(conversation)}
          >
            <Copy size={14} className="text-purple-400" />
            <span>Duplicate</span>
          </DropdownMenu.Item>

          <DropdownMenu.Item
            className="flex cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-gray-200 outline-none hover:bg-gray-800 hover:text-white"
            onClick={() => onExport?.(conversation)}
          >
            <Download size={14} className="text-emerald-400" />
            <span>Export Markdown</span>
          </DropdownMenu.Item>

          <DropdownMenu.Item
            className="flex cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-gray-200 outline-none hover:bg-gray-800 hover:text-white"
            onClick={() => onArchiveToggle?.(conversation)}
          >
            {isArchived ? (
              <>
                <RotateCcw size={14} className="text-blue-400" />
                <span>Restore chat</span>
              </>
            ) : (
              <>
                <Archive size={14} className="text-blue-400" />
                <span>Archive</span>
              </>
            )}
          </DropdownMenu.Item>

          <DropdownMenu.Separator className="my-1 h-px bg-gray-800" />

          <DropdownMenu.Item
            className="flex cursor-pointer items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-rose-400 outline-none hover:bg-rose-500/10 hover:text-rose-300"
            onClick={() => onDelete?.(conversation)}
          >
            <Trash2 size={14} />
            <span>Delete</span>
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}