import {
  UploadCloud,
  LoaderCircle,
} from "lucide-react";

export default function UploadCard({
  uploadMutation,
}) {
  function handleChange(e) {
    const file = e.target.files?.[0];

    if (!file) return;

    uploadMutation.mutate(file);

    e.target.value = "";
  }

  return (
    <label className="mb-6 flex cursor-pointer items-center justify-center rounded-2xl border-2 border-dashed border-slate-700 bg-[#131B2E] p-10 transition hover:border-blue-500">

      <input
        type="file"
        accept=".pdf"
        hidden
        onChange={handleChange}
      />

      <div className="text-center">

        {uploadMutation.isPending ? (
          <>
            <LoaderCircle
              className="mx-auto mb-4 animate-spin text-blue-500"
              size={46}
            />

            <h3 className="font-semibold text-white">
              Uploading...
            </h3>
          </>
        ) : (
          <>
            <UploadCloud
              className="mx-auto mb-4 text-blue-500"
              size={48}
            />

            <h3 className="font-semibold text-white">
              Upload PDF
            </h3>

            <p className="mt-2 text-slate-400">
              Click here to choose a PDF
            </p>
          </>
        )}

      </div>

    </label>
  );
}