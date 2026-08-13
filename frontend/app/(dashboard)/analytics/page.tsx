"use client";

import { BarChart3, Database, GitBranch, MessageSquare, TrendingUp, Activity, AlertCircle } from "lucide-react";

import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useAnalytics } from "@/hooks/use-analytics";

interface StatCardProps {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  label: string;
  value: string;
  trend?: string;
  trendUp?: boolean;
  isLoading?: boolean;
  error?: boolean;
}

function StatCard({ icon: Icon, label, value, trend, trendUp, isLoading, error }: StatCardProps) {
  if (isLoading) {
    return (
      <Card className="flex items-start gap-4 p-5">
        <div className="h-10 w-10 animate-pulse rounded-xl bg-muted" />
        <div className="flex-1 space-y-2">
          <div className="h-3 w-20 animate-pulse rounded bg-muted" />
          <div className="h-8 w-16 animate-pulse rounded bg-muted" />
          <div className="h-3 w-12 animate-pulse rounded bg-muted" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="flex items-start gap-4 p-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-destructive/10">
          <Icon size={18} className="text-destructive" />
        </div>
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="mt-1 text-2xl font-bold tracking-tight text-foreground">—</p>
          <p className="mt-1 text-xs text-destructive">Unavailable</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="flex items-start gap-4 p-5">
      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
        <Icon size={18} className="text-primary" />
      </div>
      <div className="flex-1">
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="mt-1 text-2xl font-bold tracking-tight text-foreground">{value}</p>
        {trend && (
          <p className={cn("mt-1 text-xs", trendUp ? "text-success" : "text-muted-foreground")}>
            {trend}
          </p>
        )}
      </div>
    </Card>
  );
}

export default function AnalyticsPage() {
  const { data, isLoading, isError } = useAnalytics();

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Analytics"
        description="Usage and performance metrics"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          icon={GitBranch}
          label="Indexed Repositories"
          value={data ? String(data.indexedRepositories) : "0"}
          trend={data ? `${data.indexedRepositories} total` : undefined}
          isLoading={isLoading}
          error={isError}
        />
        <StatCard
          icon={Database}
          label="Total Chunks Indexed"
          value={data ? data.totalChunks.toLocaleString() : "0"}
          isLoading={isLoading}
          error={isError}
        />
        <StatCard
          icon={MessageSquare}
          label="Queries Answered"
          value={data ? data.queriesAnswered.toLocaleString() : "0"}
          isLoading={isLoading}
          error={isError}
        />
        <StatCard
          icon={BarChart3}
          label="Avg. Query Latency"
          value={data?.avgQueryLatencyMs != null ? `${data.avgQueryLatencyMs}ms` : "—"}
          isLoading={isLoading}
          error={isError}
        />
        <StatCard
          icon={Activity}
          label="Uptime"
          value={data?.uptime ?? "—"}
          isLoading={isLoading}
          error={isError}
        />
        <StatCard
          icon={TrendingUp}
          label="Languages Supported"
          value={data ? String(data.languagesSupported) : "40+"}
          isLoading={isLoading}
          error={isError}
        />
      </div>

      <Card className="p-6">
        <h2 className="mb-4 text-sm font-semibold text-foreground">Query Volume (Last 30 Days)</h2>
        {isError ? (
          <div className="flex h-48 items-center justify-center rounded-xl bg-muted/30">
            <div className="flex flex-col items-center gap-2 text-center">
              <AlertCircle size={32} className="text-destructive" />
              <p className="text-sm text-muted-foreground">
                Unable to load analytics data. Check your backend connection.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex h-48 items-center justify-center rounded-xl bg-muted/30">
            <div className="flex flex-col items-center gap-2 text-center">
              <BarChart3 size={32} className="text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                No data yet. Start querying your repositories to see analytics.
              </p>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
