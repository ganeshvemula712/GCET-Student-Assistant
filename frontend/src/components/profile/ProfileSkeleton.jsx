export default function ProfileSkeleton() {
  return (
    <div className="space-y-6 animate-pulse max-w-5xl mx-auto">
      <div className="h-10 w-64 rounded-xl bg-gray-800" />
      <div className="h-44 w-full rounded-3xl bg-gray-800/80" />
      <div className="grid gap-6 md:grid-cols-2">
        <div className="h-80 w-full rounded-3xl bg-gray-800/70" />
        <div className="h-80 w-full rounded-3xl bg-gray-800/70" />
      </div>
    </div>
  );
}
