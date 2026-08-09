import { useMemo, useState, memo } from "react";
import { motion } from "framer-motion";
import { User, Edit3, Trash2, GraduationCap, Copy, Check } from "lucide-react";
import { toast } from "sonner";

import ConfidenceBadge from "./ConfidenceBadge";
import FollowUpSuggestions from "./FollowUpSuggestions";
import SourceCard from "./SourceCard";
import SourceModal from "./SourceModal";
import MessageToolbar from "./MessageToolbar";
import MarkdownRenderer from "./MarkdownRenderer";
import AIMetadataBar from "./AIMetadataBar";

function formatTimestamp(dateStr) {
  if (!dateStr) return "Just now";
  const date = new Date(dateStr);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function MessageBubble({
  message,
  role,
  content,
  sources = [],
  confidence,
  followUpQuestions = [],
  onEdit,
  onDelete,
  onRegenerate,
  regenerating,
  onSendFollowUp,
  onFeedback,
}) {
  const isUser = role === "user";
  const [copied, setCopied] = useState(false);
  const [userPromptCopied, setUserPromptCopied] = useState(false);
  const [selectedSource, setSelectedSource] = useState(null);
  const [feedbackValue, setFeedbackValue] = useState(null);

  const normalizedSources = useMemo(() => (sources || []).filter(Boolean), [sources]);

  async function copyText() {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function copyUserPrompt() {
    await navigator.clipboard.writeText(content);
    setUserPromptCopied(true);
    setTimeout(() => setUserPromptCopied(false), 2000);
    toast.success("User prompt copied.");
  }

  async function handleFeedback(value) {
    if (!message?.id || !onFeedback) return;
    setFeedbackValue(value);
    try {
      await onFeedback(message.id, value);
      toast.success("Feedback submitted.");
    } catch (error) {
      console.error(error);
      toast.error("Unable to save feedback.");
    }
  }

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className={`mb-6 flex ${isUser ? "justify-end" : "justify-start"}`}
      >
        {isUser ? (
          <div className="group flex max-w-5xl items-start gap-3">
            <div className="flex flex-col items-end">
              <div className="mb-1 flex items-center gap-1.5 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
                <button
                  type="button"
                  onClick={copyUserPrompt}
                  className="rounded-lg p-1 text-gray-400 hover:bg-gray-800 hover:text-white"
                  title="Copy prompt"
                >
                  {userPromptCopied ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
                </button>
                {onEdit && (
                  <button
                    type="button"
                    onClick={() => onEdit(message)}
                    className="rounded-lg p-1 text-gray-400 hover:bg-gray-800 hover:text-white"
                    title="Edit prompt"
                  >
                    <Edit3 size={13} />
                  </button>
                )}
                {onDelete && (
                  <button
                    type="button"
                    onClick={() => onDelete(message)}
                    className="rounded-lg p-1 text-gray-400 hover:bg-rose-500/20 hover:text-rose-400"
                    title="Delete message thread"
                  >
                    <Trash2 size={13} />
                  </button>
                )}
              </div>
              <div className="rounded-2xl rounded-tr-none bg-gradient-to-r from-emerald-600 to-teal-600 px-5 py-3.5 text-base font-medium text-white shadow-lg">
                <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
              </div>
              <span className="mt-1 text-[10px] text-gray-500">{formatTimestamp(message?.created_at)}</span>
            </div>
            <div className="flex size-9 shrink-0 items-center justify-center rounded-2xl border border-emerald-500/30 bg-emerald-500/20 text-emerald-400">
              <User size={18} />
            </div>
          </div>
        ) : (
          <div className="w-full max-w-6xl">
            <div className="mb-2 flex items-center gap-2.5">
              <div className="flex size-9 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-500 text-gray-950 shadow-md">
                <GraduationCap size={20} />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white">GCET AI Assistant</h4>
                <p className="text-[10px] text-gray-400">
                  {normalizedSources.length > 0 ? "RAG Knowledge Engine" : "General Knowledge AI"}
                </p>
              </div>
            </div>

            <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl backdrop-blur-sm">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-2 border-b border-gray-800/80 pb-3">
                <ConfidenceBadge score={confidence ?? 0} sourcesCount={normalizedSources.length} />
                <span className="text-[11px] font-medium text-gray-400">
                  {normalizedSources.length > 0 ? `${normalizedSources.length} Grounded Sources` : "General Knowledge"}
                </span>
              </div>

              <MarkdownRenderer content={content} />

              {normalizedSources.length > 0 && (
                <div className="mt-5 rounded-2xl border border-gray-800 bg-gray-900/60 p-4">
                  <p className="mb-3 text-xs font-bold uppercase tracking-wider text-emerald-400">
                    Grounded RAG Sources ({normalizedSources.length})
                  </p>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {normalizedSources.map((source, idx) => (
                      <SourceCard key={`${source.filename}-${idx}`} source={source} onOpen={setSelectedSource} />
                    ))}
                  </div>
                </div>
              )}

              <FollowUpSuggestions suggestions={followUpQuestions} onSelect={onSendFollowUp} />

              <AIMetadataBar
                confidence={confidence ?? 0}
                sourcesCount={normalizedSources.length}
                content={content}
              />

              <MessageToolbar
                copied={copied}
                feedbackValue={feedbackValue}
                content={content}
                onCopy={copyText}
                onFeedback={handleFeedback}
                onRegenerate={() => onRegenerate?.(message)}
                regenerating={regenerating}
              />
            </div>
          </div>
        )}
      </motion.div>

      <SourceModal open={Boolean(selectedSource)} source={selectedSource} onClose={() => setSelectedSource(null)} />
    </>
  );
}

export default memo(MessageBubble);
