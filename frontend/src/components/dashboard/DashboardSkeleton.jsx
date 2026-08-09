import SkeletonLoader from "./SkeletonLoader";

export default function DashboardSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-36 rounded-3xl bg-gray-800/60" />
      <SkeletonLoader type="card" count={4} />
      <div className="grid gap-6 lg:grid-cols-2">
        <SkeletonLoader type="list" count={4} />
        <SkeletonLoader type="list" count={4} />
      </div>
    </div>
  );
}