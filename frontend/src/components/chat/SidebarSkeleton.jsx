export default function SidebarSkeleton() {
  return (
    <div className="space-y-4 p-4 animate-pulse">
      <div className="h-10 w-full rounded-xl bg-gray-800/80" />
      <div className="h-9 w-full rounded-xl bg-gray-800/60" />
      <div className="space-y-2 pt-4">
        <div className="h-3 w-16 rounded bg-gray-800" />
        <div className="h-12 w-full rounded-xl bg-gray-800/70" />
        <div className="h-12 w-full rounded-xl bg-gray-800/70" />
        <div className="h-12 w-full rounded-xl bg-gray-800/70" />
      </div>
      <div className="space-y-2 pt-4">
        <div className="h-3 w-24 rounded bg-gray-800" />
        <div className="h-12 w-full rounded-xl bg-gray-800/70" />
        <div className="h-12 w-full rounded-xl bg-gray-800/70" />
      </div>
    </div>
  );
}
