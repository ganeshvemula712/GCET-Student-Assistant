import { Copy, Check, RefreshCw, ThumbsUp, ThumbsDown, Share2, FileDown, Printer } from "lucide-react";
import { toast } from "sonner";

export default function MessageToolbar({
  copied,
  feedbackValue,
  content = "",
  onCopy,
  onFeedback,
  onRegenerate,
  regenerating = false,
}) {
  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(content);
      toast.success("Message content copied for sharing.");
    } catch {
      toast.error("Failed to copy share link.");
    }
  };

  const handleExportMarkdown = () => {
    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "gcet_ai_response.md";
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Exported to Markdown.");
  };

  const handlePrintPDF = () => {
    window.print();
  };

  return (
    <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-gray-800/60 pt-3">
      <div className="flex flex-wrap items-center gap-1.5">
        <button
          type="button"
          onClick={onCopy}
          className="inline-flex items-center gap-1.5 rounded-lg border border-gray-800 bg-gray-900/60 px-2.5 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-gray-700 hover:bg-gray-800 hover:text-white"
          title="Copy text markdown"
        >
          {copied ? (
            <>
              <Check size={13} className="text-emerald-400" />
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy size={13} />
              <span>Copy</span>
            </>
          )}
        </button>

        {onRegenerate && (
          <button
            type="button"
            onClick={onRegenerate}
            disabled={regenerating}
            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-800 bg-gray-900/60 px-2.5 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-gray-700 hover:bg-gray-800 hover:text-white disabled:opacity-50"
            title="Regenerate response"
          >
            <RefreshCw size={13} className={regenerating ? "animate-spin text-emerald-400" : ""} />
            <span>{regenerating ? "Regenerating..." : "Regenerate"}</span>
          </button>
        )}

        <button
          type="button"
          onClick={handleShare}
          className="inline-flex items-center gap-1 rounded-lg border border-gray-800 bg-gray-900/60 px-2.5 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-gray-700 hover:bg-gray-800 hover:text-white"
          title="Share response"
        >
          <Share2 size={13} />
          <span className="hidden sm:inline">Share</span>
        </button>

        <button
          type="button"
          onClick={handleExportMarkdown}
          className="inline-flex items-center gap-1 rounded-lg border border-gray-800 bg-gray-900/60 px-2.5 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-gray-700 hover:bg-gray-800 hover:text-white"
          title="Export as Markdown"
        >
          <FileDown size={13} />
          <span className="hidden sm:inline">.MD</span>
        </button>

        <button
          type="button"
          onClick={handlePrintPDF}
          className="inline-flex items-center gap-1 rounded-lg border border-gray-800 bg-gray-900/60 px-2.5 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-gray-700 hover:bg-gray-800 hover:text-white"
          title="Print / Save PDF"
        >
          <Printer size={13} />
        </button>
      </div>

      {onFeedback && (
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => onFeedback("positive")}
            className={`rounded-lg p-1.5 transition-colors ${
              feedbackValue === "positive"
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
            }`}
            title="Helpful response"
          >
            <ThumbsUp size={14} />
          </button>
          <button
            type="button"
            onClick={() => onFeedback("negative")}
            className={`rounded-lg p-1.5 transition-colors ${
              feedbackValue === "negative"
                ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
            }`}
            title="Unhelpful response"
          >
            <ThumbsDown size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
