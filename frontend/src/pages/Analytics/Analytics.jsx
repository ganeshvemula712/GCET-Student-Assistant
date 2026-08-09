import { useState } from "react";
import { AlertCircle } from "lucide-react";
import AnalyticsHeader from "@/components/analytics/AnalyticsHeader";
import OverviewCards from "@/components/analytics/OverviewCards";
import ConversationChart from "@/components/analytics/ConversationChart";
import AIConfidenceBreakdown from "@/components/analytics/AIConfidenceBreakdown";
import DocumentStatsCard from "@/components/analytics/DocumentStatsCard";
import AnalyticsSkeleton from "@/components/analytics/AnalyticsSkeleton";

import useAnalyticsSummary from "@/hooks/useAnalyticsSummary";

export default function Analytics() {
  const [days, setDays] = useState(30);
  const { data, isLoading, isError, refetch } = useAnalyticsSummary(days);

  if (isLoading) {
    return <AnalyticsSkeleton />;
  }

  if (isError) {
    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-center text-sm font-semibold text-rose-400 shadow-xl">
        <AlertCircle size={32} className="mx-auto mb-2 text-rose-400" />
        Failed to load application analytics data. Please check your network connection and try again.
        <div className="mt-4">
          <button
            onClick={() => refetch()}
            className="rounded-2xl bg-rose-500 px-5 py-2 text-xs font-bold text-white shadow-md hover:bg-rose-400"
          >
            Retry Analytics Sync
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto space-y-8 pb-12">
      <AnalyticsHeader days={days} onDaysChange={setDays} />

      <OverviewCards data={data} />

      <ConversationChart
        conversationsOverTime={data?.conversations_over_time || []}
        messagesOverTime={data?.messages_over_time || []}
      />

      <div className="grid gap-8 lg:grid-cols-2">
        <AIConfidenceBreakdown data={data} />
        <DocumentStatsCard data={data} />
      </div>
    </div>
  );
}
