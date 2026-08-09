export default function DeleteDialog({
  open,
  filename,
  onCancel,
  onConfirm,
  loading,
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">

      <div className="w-full max-w-md rounded-2xl bg-slate-900 p-6">

        <h2 className="text-xl font-bold text-white">
          Delete Document
        </h2>

        <p className="mt-4 text-slate-400">
          Are you sure you want to delete
          <span className="font-semibold text-white">
            {" "}
            {filename}
          </span>
          ?
        </p>

        <div className="mt-8 flex justify-end gap-3">

          <button
            onClick={onCancel}
            className="rounded-xl border border-slate-700 px-5 py-2"
          >
            Cancel
          </button>

          <button
            disabled={loading}
            onClick={onConfirm}
            className="rounded-xl bg-red-600 px-5 py-2 text-white"
          >
            Delete
          </button>

        </div>

      </div>

    </div>
  );
}