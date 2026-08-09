import { AlertCircle, RefreshCw } from "lucide-react";

export default function AIErrorBanner({
  message = "Unable to generate a response. Please check your network or try again.",
  onRetry,
}) {
  return (
    <div className="my-4 flex items-center justify-between rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs text-rose-300 shadow-lg">
      <div className="flex items-center gap-2.5">
        <AlertCircle size={18} className="shrink-0 text-rose-400" />
        <p className="font-medium leading-relaxed">{message}</p>
      </div>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="ml-3 inline-flex shrink-0 items-center gap-1.5 rounded-xl border border-rose-500/40 bg-rose-500/20 px-3 py-1.5 font-semibold text-white transition hover:bg-rose-500/30"
        >
          <RefreshCw size={13} />
          <span>Retry</span>
        </button>
      )}
    </div>
  );
}
