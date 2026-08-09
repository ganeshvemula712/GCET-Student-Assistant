export default function AdminSkeleton() {
  return (
    <div className="space-y-6 animate-pulse max-w-6xl mx-auto">
      <div className="h-10 w-64 rounded-xl bg-gray-800" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-28 rounded-3xl bg-gray-800/80" />
        ))}
      </div>
      <div className="h-96 w-full rounded-3xl bg-gray-800/70" />
    </div>
  );
}
