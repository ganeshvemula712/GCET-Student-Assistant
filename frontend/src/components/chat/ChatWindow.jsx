import { useEffect, useMemo, useState, useCallback } from "react";
import useConversation from "@/hooks/useConversation";
import useDeleteMessage from "@/hooks/useDeleteMessage";
import useRegenerateMessage from "@/hooks/useRegenerateMessage";
import useChat from "@/hooks/useChat";
import useAbortChat from "@/hooks/useAbortChat";
import useAutoScroll from "@/hooks/useAutoScroll";
import { submitFeedback } from "@/services/feedbackService";
import { ArrowDown } from "lucide-react";

import ChatHeader from "./ChatHeader";
import ChatInput from "./ChatInput";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import WelcomeScreen from "./WelcomeScreen";
import ChatSkeletonLoader from "./ChatSkeletonLoader";
import MemoryIndicator from "./MemoryIndicator";
import AIErrorBanner from "./AIErrorBanner";

export default function ChatWindow({
  conversationId,
  onSelectConversation,
  editingMessage,
  clearEditing,
  onEdit,
  onToggleSidebar,
  onNewChat,
}) {
  const isNewChatState = conversationId === "new" || !conversationId;
  const activeConvId = isNewChatState ? null : conversationId;

  const { data, isLoading, isError, refetch } = useConversation(activeConvId);
  const deleteMutation = useDeleteMessage();
  const regenerateMutation = useRegenerateMessage();
  const chatMutation = useChat();
  const { createController, clearController } = useAbortChat();

  const [streamingAnswer, setStreamingAnswer] = useState("");
  const [streamingMetadata, setStreamingMetadata] = useState({ confidence: 0, followUpQuestions: [] });
  const [streamingMessageId, setStreamingMessageId] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState(null);
  const [suggestedQuestion, setSuggestedQuestion] = useState("");

  // Stable UUID generated per "new chat" session
  const newSessionUUID = useMemo(() => {
    return crypto.randomUUID();
  }, [conversationId]);

  const targetConvId = activeConvId || newSessionUUID;

  const { containerRef, bottomSentinelRef, isAtBottom, scrollToBottom } = useAutoScroll({
    enabled: isStreaming,
    dependency: `${targetConvId}-${streamingAnswer}`,
  });

  const conversationStats = useMemo(() => {
    const messages = data?.messages || [];
    const assistantMessages = messages.filter((message) => message.role === "assistant");
    const confidences = assistantMessages
      .map((message) => Number(message.confidence || 0))
      .filter((value) => Number.isFinite(value));

    const averageConfidence = confidences.length
      ? Math.round(confidences.reduce((sum, value) => sum + value, 0) / confidences.length)
      : 0;

    return {
      totalMessages: messages.length,
      retrievedDocuments: messages.reduce((sum, message) => sum + (message.sources?.length || 0), 0),
      averageConfidence,
      lastUpdated: messages.at(-1)?.created_at || data?.created_at || null,
    };
  }, [data]);

  useEffect(() => {
    setStreamingAnswer("");
    setStreamingMessageId(null);
    setIsStreaming(false);
    setStreamError(null);
    setStreamingMetadata({ confidence: 0, followUpQuestions: [] });
  }, [conversationId]);

  const handleDelete = useCallback(
    async (message) => {
      if (!activeConvId) return;
      const confirmed = window.confirm("Delete this message and all following messages in thread?");
      if (!confirmed) return;

      try {
        await deleteMutation.mutateAsync({
          messageId: message.id,
          conversationId: activeConvId,
        });

        if (editingMessage?.id === message.id) {
          clearEditing();
        }
      } catch (err) {
        console.error(err);
      }
    },
    [deleteMutation, activeConvId, editingMessage, clearEditing]
  );

  const handleRegenerate = useCallback(
    async (message) => {
      if (!activeConvId || !message?.id) return;
      try {
        setStreamError(null);

        // 1. Reset assistant message in DB & get user question
        const regRes = await regenerateMutation.mutateAsync({
          messageId: message.id,
          conversationId: activeConvId,
        });

        const userQuestion = regRes?.user_question || data?.messages?.find((m) => m.role === "user")?.content;
        if (!userQuestion) {
          throw new Error("User question not found for regeneration");
        }

        // 2. Stream new response through unified AI pipeline
        const controller = createController();
        setIsStreaming(true);
        setStreamingAnswer("");
        setStreamingMessageId(`stream-${activeConvId}`);

        await chatMutation.mutateAsync({
          conversationId: activeConvId,
          question: userQuestion,
          token: localStorage.getItem("access_token"),
          signal: controller.signal,
          onChunk: (text) => {
            setStreamError(null);
            setStreamingAnswer(text);
          },
          onComplete: (result, wasAborted, metadata) => {
            if (!wasAborted) {
              setStreamingMetadata({
                confidence: metadata?.confidence ?? 0,
                followUpQuestions: metadata?.follow_up_questions ?? [],
              });
            }
            setStreamingAnswer("");
            setStreamingMessageId(null);
            setIsStreaming(false);
            clearController();
          },
          onAbort: () => {
            setStreamingAnswer("");
            setStreamingMessageId(null);
            setIsStreaming(false);
            clearController();
          },
        });
      } catch (err) {
        console.error(err);
        setIsStreaming(false);
        setStreamError("Sorry, I couldn't generate a response right now. Please try again.");
        clearController();
      }
    },
    [regenerateMutation, chatMutation, activeConvId, data, createController, clearController]
  );

  const handleRetryLastPrompt = useCallback(async () => {
    const messages = data?.messages || [];
    const lastUserMsg = [...messages].reverse().find((m) => m.role === "user");
    if (!lastUserMsg?.content || !activeConvId) return;

    setStreamError(null);
    const controller = createController();
    setIsStreaming(true);
    setStreamingAnswer("");
    setStreamingMessageId(`stream-${activeConvId}`);

    try {
      await chatMutation.mutateAsync({
        conversationId: activeConvId,
        question: lastUserMsg.content,
        token: localStorage.getItem("access_token"),
        signal: controller.signal,
        onChunk: (text) => {
          setStreamError(null);
          setStreamingAnswer(text);
        },
        onComplete: (result, wasAborted, metadata) => {
          if (!wasAborted) {
            setStreamingMetadata({
              confidence: metadata?.confidence ?? 0,
              followUpQuestions: metadata?.follow_up_questions ?? [],
            });
          }
          setStreamingAnswer("");
          setStreamingMessageId(null);
          setIsStreaming(false);
          clearController();
        },
        onAbort: () => {
          setStreamingAnswer("");
          setStreamingMessageId(null);
          setIsStreaming(false);
          clearController();
        },
      });
    } catch (err) {
      console.error(err);
      setIsStreaming(false);
      setStreamError("Sorry, I couldn't generate a response right now. Please try again.");
      clearController();
    }
  }, [data, activeConvId, chatMutation, createController, clearController]);

  return (
    <div className="flex h-full flex-1 flex-col bg-[#0B1020] relative">
      <ChatHeader
        onToggleSidebar={onToggleSidebar}
        onNewChat={onNewChat}
        totalMessages={conversationStats.totalMessages}
      />

      <div ref={containerRef} className="flex-1 overflow-y-auto px-4 py-6 sm:px-8 relative">
        {isLoading && activeConvId ? (
          <ChatSkeletonLoader />
        ) : isNewChatState || !data?.messages?.length ? (
          <WelcomeScreen onSelectPrompt={(promptText) => setSuggestedQuestion(promptText)} />
        ) : (
          <>
            <MemoryIndicator messageCount={conversationStats.totalMessages} retrievedCount={conversationStats.retrievedDocuments} />

            {data.messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                role={message.role}
                content={message.content}
                sources={message.sources || []}
                confidence={message.confidence}
                followUpQuestions={message.follow_up_questions || []}
                onEdit={onEdit}
                onDelete={handleDelete}
                onRegenerate={handleRegenerate}
                regenerating={regenerateMutation.isPending || (isStreaming && streamingMessageId === `stream-${activeConvId}`)}
                onFeedback={submitFeedback}
                onSendFollowUp={setSuggestedQuestion}
              />
            ))}

            {isStreaming && !streamingAnswer && <TypingIndicator />}

            {streamingAnswer && (
              <MessageBubble
                key={streamingMessageId ?? `stream-${targetConvId}`}
                message={{ id: streamingMessageId ?? `stream-${targetConvId}` }}
                role="assistant"
                content={streamingAnswer}
                sources={[]}
                confidence={streamingMetadata.confidence}
                followUpQuestions={streamingMetadata.followUpQuestions}
              />
            )}

            {(isError || streamError) && (
              <AIErrorBanner
                message={streamError || "Sorry, I couldn't generate a response right now. Please try again."}
                onRetry={handleRetryLastPrompt}
              />
            )}

            {/* Bottom Sentinel Ref for ChatGPT Auto-Scroll */}
            <div ref={bottomSentinelRef} className="h-6 w-full shrink-0" />
          </>
        )}
      </div>

      {/* Floating Jump to Latest Button when user manually scrolls up */}
      {!isAtBottom && (
        <button
          type="button"
          onClick={() => scrollToBottom("smooth")}
          className="absolute bottom-24 right-8 z-30 flex items-center gap-2 rounded-full border border-emerald-500/30 bg-[#0F172A]/90 px-4 py-2 text-xs font-bold text-emerald-400 shadow-2xl backdrop-blur-md hover:bg-[#1E293B] hover:text-white transition duration-200"
        >
          <ArrowDown size={14} className="animate-bounce" />
          <span>Jump to latest</span>
        </button>
      )}

      {/* Metadata strip */}
      <div className="border-t border-gray-800/80 bg-gray-950/90 px-4 py-1 text-[11px] text-gray-400">
        <div className="flex flex-wrap items-center justify-between gap-3 max-w-6xl mx-auto">
          <div className="flex items-center gap-3">
            <span>Messages: <strong className="text-white">{conversationStats.totalMessages}</strong></span>
            <span>Ground Sources: <strong className="text-emerald-400">{conversationStats.retrievedDocuments}</strong></span>
            <span>Avg Confidence: <strong className="text-cyan-400">{conversationStats.averageConfidence}%</strong></span>
          </div>
          <span className="hidden md:inline">
            Engine: <strong className="text-gray-300">Gemini 2.5 Flash + ChromaDB</strong>
          </span>
        </div>
      </div>

      {/* Message Composer */}
      <div className="sticky bottom-0 z-10 bg-[#0B1020]">
        <ChatInput
          conversationId={targetConvId}
          onEnsureConversation={() => {
            if (isNewChatState) {
              onSelectConversation?.(targetConvId);
            }
          }}
          editingMessage={editingMessage}
          clearEditing={clearEditing}
          onStream={(text) => {
            if (isNewChatState) {
              onSelectConversation?.(targetConvId);
            }
            setStreamError(null);
            setStreamingAnswer(text);
            setStreamingMessageId((current) => current ?? `stream-${targetConvId}`);
          }}
          onStreamComplete={(result, wasAborted, metadata) => {
            if (wasAborted) {
              setStreamingAnswer("");
              setStreamingMessageId(null);
              setStreamingMetadata({ confidence: 0, followUpQuestions: [] });
              setIsStreaming(false);
              return;
            }

            setStreamingMetadata({
              confidence: metadata?.confidence ?? 0,
              followUpQuestions: metadata?.follow_up_questions ?? [],
            });
            setStreamingAnswer("");
            setStreamingMessageId(null);
            setIsStreaming(false);
          }}
          onStreamStateChange={setIsStreaming}
          suggestedQuestion={suggestedQuestion}
          onSuggestedQuestionUsed={() => setSuggestedQuestion("")}
        />
      </div>
    </div>
  );
}
