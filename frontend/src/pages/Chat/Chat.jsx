import { useState, useCallback, useRef, useEffect } from "react";
import ChatSidebar from "@/components/chat/ChatSidebar";
import ChatWindow from "@/components/chat/ChatWindow";
import { GripVertical } from "lucide-react";

export default function Chat() {
  const [conversationId, setConversationId] = useState(null);
  const [editingMessage, setEditingMessage] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(280);
  const [isResizing, setIsResizing] = useState(false);
  const isDraggingRef = useRef(false);

  const startResizing = useCallback((e) => {
    e.preventDefault();
    isDraggingRef.current = true;
    setIsResizing(true);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDraggingRef.current) return;
      // Calculate width relative to chat container
      const newWidth = Math.min(Math.max(e.clientX - 224, 240), 420);
      setSidebarWidth(newWidth);
    };

    const handleMouseUp = () => {
      if (isDraggingRef.current) {
        isDraggingRef.current = false;
        setIsResizing(false);
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, []);

  return (
    <div className="flex h-full min-h-0 flex-1 w-full overflow-hidden rounded-xl md:rounded-3xl border border-gray-800 bg-[#0B1120] shadow-2xl relative select-none">
      {/* Mobile Overlay */}
      <div
        className={`fixed inset-0 z-40 bg-black/60 backdrop-blur-sm transition-opacity md:hidden ${
          sidebarOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        }`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar Panel */}
      <div
        style={{ width: `${sidebarWidth}px` }}
        className={`fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 md:static md:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <ChatSidebar
          selectedConversation={conversationId}
          onSelectConversation={(id) => {
            setConversationId(id);
            setSidebarOpen(false);
          }}
          style={{ width: "100%" }}
        />
      </div>

      {/* Draggable Vertical Divider (Desktop Only) */}
      <div
        onMouseDown={startResizing}
        className={`hidden md:flex w-1.5 cursor-col-resize items-center justify-center bg-gray-900 transition-colors hover:bg-emerald-500/50 active:bg-emerald-500 ${
          isResizing ? "bg-emerald-500" : ""
        }`}
        title="Drag to resize conversation history width"
      >
        <GripVertical size={12} className="text-gray-600 hover:text-white" />
      </div>

      {/* Main Conversation Window */}
      <ChatWindow
        conversationId={conversationId}
        onSelectConversation={setConversationId}
        editingMessage={editingMessage}
        clearEditing={() => setEditingMessage(null)}
        onEdit={setEditingMessage}
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        onNewChat={() => {
          setConversationId(null);
          setEditingMessage(null);
        }}
      />
    </div>
  );
}