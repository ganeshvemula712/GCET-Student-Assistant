export default function DocumentSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 animate-pulse">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div key={i} className="rounded-2xl border border-gray-800 bg-[#111827] p-5">
          <div className="flex items-center gap-3">
            <div className="size-10 rounded-xl bg-gray-800" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-3/4 rounded bg-gray-800" />
              <div className="h-3 w-1/2 rounded bg-gray-800/60" />
            </div>
          </div>
          <div className="mt-4 flex gap-2 pt-2">
            <div className="h-6 w-16 rounded-full bg-gray-800" />
            <div className="h-6 w-16 rounded-full bg-gray-800" />
          </div>
          <div className="mt-4 h-8 w-full rounded-xl bg-gray-800/80" />
        </div>
      ))}
    </div>
  );
}
