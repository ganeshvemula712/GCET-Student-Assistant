import { useEffect, useRef, useState } from "react";
import { ArrowUp, CircleNotch, X } from "@phosphor-icons/react";
import { toast } from "sonner";

import useAbortChat from "@/hooks/useAbortChat";
import useChat from "@/hooks/useChat";
import useUpdateMessage from "@/hooks/useUpdateMessage";

export default function ChatInput({
  conversationId,
  onEnsureConversation,
  editingMessage,
  clearEditing,
  onStream,
  onStreamComplete,
  onStreamStateChange,
  suggestedQuestion,
  onSuggestedQuestionUsed,
}) {
  const [question, setQuestion] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef(null);

  const chatMutation = useChat();
  const updateMutation = useUpdateMessage();
  const { createController, abortActiveRequest, clearController } = useAbortChat();

  const isGenerating = chatMutation.isPending || updateMutation.isPending;

  useEffect(() => {
    if (editingMessage) {
      setQuestion(editingMessage.content);
    }
  }, [editingMessage]);

  useEffect(() => {
    if (suggestedQuestion) {
      setQuestion(suggestedQuestion);
      onSuggestedQuestionUsed?.();
    }
  }, [suggestedQuestion, onSuggestedQuestionUsed]);

  useEffect(() => {
    onStreamStateChange?.(isGenerating);
  }, [isGenerating, onStreamStateChange]);

  useEffect(() => {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";
    const maxHeight = 8 * 24;
    textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
    textarea.style.overflowY = textarea.scrollHeight > maxHeight ? "auto" : "hidden";
  }, [question]);

  async function submitQuestion() {
    if (isGenerating || !question.trim()) {
      return;
    }

    const previousQuestion = question;
    const trimmedQuestion = question.trim();

    setErrorMessage("");
    const controller = createController();

    try {
      if (editingMessage) {
        if (!editingMessage?.id) {
          throw new Error("Unable to edit message: missing message ID");
        }

        // 1. Update user question in database & delete old answer thread
        const updateRes = await updateMutation.mutateAsync({
          messageId: editingMessage.id,
          content: trimmedQuestion,
          conversationId,
        });

        // 2. Reset input and close editing banner
        setQuestion("");
        clearEditing?.();

        // 3. Stream new response through standard chat pipeline
        const targetConvId = updateRes?.conversation_id || conversationId;
        onEnsureConversation?.();

        await chatMutation.mutateAsync({
          conversationId: targetConvId,
          question: trimmedQuestion,
          token: localStorage.getItem("access_token"),
          signal: controller.signal,
          onChunk: (text) => {
            onStream?.(text);
          },
          onComplete: (result, wasAborted, metadata) => {
            onStreamComplete?.(result, wasAborted, metadata);
            clearController();
          },
          onAbort: (result) => {
            onStreamComplete?.(result, true);
            clearController();
          },
        });
        return;
      }

      onEnsureConversation?.();

      await chatMutation.mutateAsync({
        conversationId,
        question: trimmedQuestion,
        token: localStorage.getItem("access_token"),
        signal: controller.signal,
        onChunk: (text) => {
          onStream?.(text);
        },
        onComplete: (result, wasAborted, metadata) => {
          onStreamComplete?.(result, wasAborted, metadata);
          clearController();
        },
        onAbort: (result) => {
          onStreamComplete?.(result, true);
          clearController();
        },
      });

      setQuestion("");
      clearEditing?.();
    } catch (err) {
      if (err?.name === "AbortError") {
        clearController();
        return;
      }

      console.error(err);
      setQuestion(previousQuestion);
      setErrorMessage("Sorry, I couldn't generate a response right now. Please try again.");
      toast.error("Sorry, I couldn't generate a response right now. Please try again.");
      clearController();
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    void submitQuestion();
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey && !isComposing) {
      e.preventDefault();
      void submitQuestion();
    }
  }

  function handleStopGeneration() {
    if (!isGenerating) {
      return;
    }

    abortActiveRequest();
    setErrorMessage("");
  }

  return (
    <div className="border-t border-white/10 bg-[#020817] px-6 py-4">
      <div className="max-w-6xl mx-auto space-y-3">
        {editingMessage && (
          <div className="mb-4 flex items-center justify-between rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3">
            <div>
              <p className="text-sm font-medium text-amber-300">Editing your question</p>
              <p className="text-xs text-gray-400">Update your question and click Send to generate a new AI response.</p>
            </div>

            <button onClick={clearEditing} className="text-gray-400 hover:text-white">
              <X size={18} />
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="flex items-end gap-3 rounded-3xl border border-white/10 bg-slate-900 p-3">
            <textarea
              ref={textareaRef}
              rows={1}
              value={question}
              disabled={isGenerating}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              onCompositionStart={() => setIsComposing(true)}
              onCompositionEnd={() => setIsComposing(false)}
              placeholder={editingMessage ? "Edit your question..." : "Ask anything about GCET..."}
              className="flex-1 resize-none bg-transparent px-3 py-2 text-white outline-none disabled:cursor-not-allowed disabled:opacity-70"
            />

            {isGenerating ? (
              <button
                type="button"
                onClick={handleStopGeneration}
                className="flex min-w-[110px] items-center justify-center gap-2 rounded-full bg-amber-500 px-4 py-3 font-medium text-slate-950 transition hover:bg-amber-400 cursor-pointer"
              >
                <CircleNotch size={18} className="animate-spin" />
                <span>Stop</span>
              </button>
            ) : (
              <button
                type="submit"
                disabled={!question.trim()}
                className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-600 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
              >
                <ArrowUp size={20} weight="bold" />
              </button>
            )}
          </div>

          {errorMessage && (
            <p className="mt-3 text-sm text-rose-400" role="alert">
              {errorMessage}
            </p>
          )}
        </form>
      </div>
    </div>
  );
}
