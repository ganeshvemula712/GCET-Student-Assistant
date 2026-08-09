export default function AnalyticsSkeleton() {
  return (
    <div className="space-y-6 animate-pulse max-w-6xl mx-auto">
      <div className="h-10 w-64 rounded-xl bg-gray-800" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-28 rounded-3xl bg-gray-800/80" />
        ))}
      </div>
      <div className="h-80 w-full rounded-3xl bg-gray-800/70" />
      <div className="grid gap-6 md:grid-cols-2">
        <div className="h-64 w-full rounded-3xl bg-gray-800/70" />
        <div className="h-64 w-full rounded-3xl bg-gray-800/70" />
      </div>
    </div>
  );
}
