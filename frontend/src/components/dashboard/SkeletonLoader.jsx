export default function SkeletonLoader({ type = "card", count = 1 }) {
  const items = Array.from({ length: count });

  if (type === "card") {
    return (
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {items.map((_, i) => (
          <div
            key={i}
            className="h-36 animate-pulse rounded-2xl border border-gray-800 bg-[#111827] p-6 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div className="space-y-3">
                <div className="h-4 w-24 rounded bg-gray-800" />
                <div className="h-8 w-16 rounded bg-gray-800" />
                <div className="h-3 w-20 rounded bg-gray-800" />
              </div>
              <div className="size-12 rounded-xl bg-gray-800" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (type === "list") {
    return (
      <div className="space-y-3">
        {items.map((_, i) => (
          <div
            key={i}
            className="flex items-center justify-between rounded-xl border border-gray-800/80 bg-[#111827]/80 p-4"
          >
            <div className="space-y-2">
              <div className="h-4 w-40 rounded bg-gray-800" />
              <div className="h-3 w-24 rounded bg-gray-800" />
            </div>
            <div className="size-6 rounded-full bg-gray-800" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="h-28 w-full animate-pulse rounded-2xl bg-gray-800/60" />
  );
}
