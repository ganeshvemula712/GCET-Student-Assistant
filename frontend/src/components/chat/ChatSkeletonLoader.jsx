export default function ChatSkeletonLoader() {
  return (
    <div className="space-y-6 px-6 py-6 animate-pulse">
      {/* User message skeleton */}
      <div className="flex justify-end">
        <div className="h-14 w-2/3 rounded-2xl bg-gray-800/80" />
      </div>

      {/* Assistant message skeleton */}
      <div className="flex justify-start">
        <div className="w-full max-w-3xl space-y-4 rounded-3xl border border-gray-800 bg-[#111827] p-6">
          <div className="flex items-center gap-3">
            <div className="size-10 rounded-2xl bg-gray-800" />
            <div className="space-y-2">
              <div className="h-4 w-32 rounded bg-gray-800" />
              <div className="h-3 w-20 rounded bg-gray-800" />
            </div>
          </div>
          <div className="space-y-3 pt-2">
            <div className="h-4 w-full rounded bg-gray-800" />
            <div className="h-4 w-5/6 rounded bg-gray-800" />
            <div className="h-4 w-4/6 rounded bg-gray-800" />
          </div>
        </div>
      </div>
    </div>
  );
}
