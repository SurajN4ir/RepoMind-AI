"use client";

import { useParams, usePathname } from "next/navigation";
import {
  FileText,
  MessageSquare,
  Search,
  AlertCircle,
  Files,
  Clock,
  CheckCircle2,
  Activity as ActivityIcon,
  BarChart3,
  GitBranch,
} from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MetricCard } from "@/components/dashboard/metric-card";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { cn } from "@/lib/utils";
import { useRepository } from "@/hooks/use-repositories";
import { useRepositoryActivity } from "@/hooks/use-repository-activity";
import { useIndexRepository } from "@/hooks/use-index-repository";
import { useToast } from "@/providers/toast-provider";
import { ROUTES } from "@/lib/constants";

const tabs = [
  { label: "Overview", href: "", icon: BarChart3 },
  { label: "Files", href: "files", icon: FileText },
  { label: "Graph", href: "graph", icon: GitBranch },
  { label: "Chat", href: "chat", icon: MessageSquare },
  { label: "Search", href: "search", icon: Search },
];

function formatRelativeTime(isoString: string | null): string {
  if (!isoString) return "Never";
  const now = Date.now();
  const then = new Date(isoString).getTime();
  const seconds = Math.floor((now - then) / 1000);
  if (seconds < 60) return "Just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours > 1 ? "s" : ""} ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days} day${days > 1 ? "s" : ""} ago`;
  return new Date(isoString).toLocaleDateString();
}

function isIndexed(status: string): boolean {
  return status === "ready" || status === "READY";
}

function primaryLanguage(summary: Record<string, number> | null): string | null {
  if (summary == null) return null;
  const entries = Object.entries(summary).sort(([, a], [, b]) => b - a);
  return entries[0]?.[0] ?? null;
}

export default function RepositoryOverviewPage() {
  const params = useParams();
  const pathname = usePathname();
  const repoId = params.repositoryId as string;
  const { data: repo, isLoading, isError } = useRepository(repoId);
  const { data: activity } = useRepositoryActivity(repoId);

  const activeTab = pathname.endsWith(`/${repoId}`)
    ? ""
    : tabs
        .map((t) => t.href)
        .find((href) => href && pathname.includes(`/${repoId}/${href}`)) ?? "";

  const { toast } = useToast();
  const indexed = repo ? isIndexed(repo.status) : false;
  const lastIndexed = repo?.last_indexed_at ?? null;
  const totalFiles = repo?.total_files ?? null;
  const indexedFileCount = repo?.indexed_file_count ?? null;
  const defaultBranch = repo?.default_branch ?? null;
  const topLanguage = repo ? primaryLanguage(repo.language_summary) : null;
  const canIndex = repo && !isIndexed(repo.status) && repo.status !== "INDEXING";
  const indexMutation = useIndexRepository();

  if (isError) {
    return (
      <div className="flex flex-col gap-6">
        <PageHeader title="Repository" description="" />
        <Card className="flex flex-col items-center gap-4 px-6 py-16 text-center">
          <AlertCircle size={40} className="text-destructive" />
          <p className="text-sm text-muted-foreground">
            Failed to load repository. It may not exist or you don&rsquo;t have access.
          </p>
          <Link href={ROUTES.dashboard}>
            <Button variant="secondary">Back to repositories</Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={repo?.name ?? "Repository"}
        description={repo?.description ?? undefined}
        action={
          repo && (
            <span
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium",
                indexed
                  ? "bg-success/10 text-success"
                  : "bg-warning/10 text-warning",
              )}
            >
              <span
                className={cn(
                  "h-1.5 w-1.5 rounded-full",
                  indexed ? "bg-success" : "bg-warning",
                )}
              />
              {indexed ? "Indexed" : "Indexing..."}
            </span>
          )
        }
        isLoading={isLoading}
      />

      <div className="flex gap-1 border-b border-border">
        {tabs.map((tab) => (
          <Link
            key={tab.href}
            href={`${ROUTES.dashboard}/${repoId}${tab.href ? `/${tab.href}` : ""}`}
            className={cn(
              "flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors",
              "hover:text-foreground",
              tab.href === activeTab
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground",
            )}
          >
            <tab.icon size={16} />
            {tab.label}
          </Link>
        ))}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Files Indexed"
          value={indexedFileCount != null ? indexedFileCount.toLocaleString() : "—"}
          icon={<Files size={18} />}
          isLoading={isLoading}
        />
        <MetricCard
          label="Last Indexed"
          value={formatRelativeTime(lastIndexed ?? null)}
          icon={<Clock size={18} />}
          trend={{ direction: "neutral", label: indexed ? "Auto-sync on" : "Pending" }}
          isLoading={isLoading}
        />
        <MetricCard
          label="Index Coverage"
          value={totalFiles != null && totalFiles > 0 ? `${Math.round(((indexedFileCount ?? 0) / totalFiles) * 100)}%` : "—"}
          icon={<CheckCircle2 size={18} />}
          isLoading={isLoading}
        />
        <MetricCard
          label="Processing"
          value={indexed ? "Idle" : "Active"}
          icon={<ActivityIcon size={18} />}
          trend={{
            direction: indexed ? "neutral" : "up",
            label: indexed ? "All up to date" : "Indexing in progress",
          }}
          isLoading={isLoading}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="flex flex-col gap-4 lg:col-span-2">
          <ActivityFeed items={activity ?? []} isLoading={isLoading} />

          <Card className="p-5">
            <h3 className="mb-4 text-sm font-semibold text-foreground">Quick Actions</h3>
            <div className="flex flex-wrap gap-3">
              {canIndex && (
                <Button
                  variant="default"
                  className="gap-2"
                  disabled={indexMutation.isPending}
                  onClick={() => {
                    indexMutation.mutate(repoId, {
                      onSuccess: (data) => {
                        if (data.success) {
                          toast("Repository indexed successfully", "success");
                        } else {
                          toast(
                            `Indexing completed with errors: ${data.errors.join(", ")}`,
                            "error",
                          );
                        }
                      },
                      onError: (err) => {
                        toast(
                          err instanceof Error ? err.message : "Failed to index repository",
                          "error",
                        );
                      },
                    });
                  }}
                >
                  <ActivityIcon size={16} />
                  {indexMutation.isPending ? "Indexing..." : "Start Indexing"}
                </Button>
              )}
              <Link href={`${ROUTES.dashboard}/${repoId}/graph`}>
                <Button variant="secondary" className="gap-2">
                  <GitBranch size={16} />
                  View Dependency Graph
                </Button>
              </Link>
              <Link href={`${ROUTES.dashboard}/${repoId}/chat`}>
                <Button variant="secondary" className="gap-2">
                  <MessageSquare size={16} />
                  Chat with Repo
                </Button>
              </Link>
              <Link href={`${ROUTES.dashboard}/${repoId}/search`}>
                <Button variant="secondary" className="gap-2">
                  <Search size={16} />
                  Search Codebase
                </Button>
              </Link>
            </div>
          </Card>
        </div>

        <div className="flex flex-col gap-4">
          <Card className="p-5">
            <h3 className="mb-4 text-sm font-semibold text-foreground">Details</h3>
            {isLoading ? (
              <div className="space-y-3">
                <div className="h-4 w-full animate-pulse rounded bg-muted" />
                <div className="h-4 w-2/3 animate-pulse rounded bg-muted" />
              </div>
            ) : (
              <dl className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Default branch</dt>
                  <dd className="font-mono text-foreground">{defaultBranch ?? "main"}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Language</dt>
                  <dd className="text-foreground">{topLanguage ?? "—"}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Status</dt>
                  <dd>
                    {indexed ? (
                      <span className="text-success">Indexed</span>
                    ) : (
                      <span className="text-warning">Pending</span>
                    )}
                  </dd>
                </div>
                {totalFiles != null && (
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Total files</dt>
                    <dd className="text-foreground">{totalFiles.toLocaleString()}</dd>
                  </div>
                )}
              </dl>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
