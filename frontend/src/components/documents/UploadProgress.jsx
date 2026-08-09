import { LoaderCircle } from "lucide-react";

export default function UploadProgress({
  progress,
  filename,
}) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">

      <div className="mb-4 flex items-center gap-3">

        <LoaderCircle
          className="animate-spin text-blue-500"
          size={22}
        />

        <div>

          <h3 className="font-semibold text-white">
            Uploading...
          </h3>

          <p className="text-sm text-slate-400">
            {filename}
          </p>

        </div>

      </div>

      <div className="h-3 overflow-hidden rounded-full bg-slate-800">

        <div
          className="h-full rounded-full bg-blue-600 transition-all duration-300"
          style={{
            width: `${progress}%`,
          }}
        />

      </div>

      <p className="mt-2 text-right text-sm text-slate-400">
        {progress}%
      </p>

    </div>
  );
}