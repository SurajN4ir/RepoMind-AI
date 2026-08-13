"use client";

import { useState } from "react";
import { GitBranch, Plus, RefreshCw, FileText } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useRepositories } from "@/hooks/use-repositories";
import { ROUTES } from "@/lib/constants";
import { AddRepositoryDialog } from "@/features/repository/components/add-repository-dialog";

function isIndexed(status: string): boolean {
  return status === "ready" || status === "READY";
}

function primaryLanguage(summary: Record<string, number> | null): string | null {
  if (summary == null) return null;
  const entries = Object.entries(summary).sort(([, a], [, b]) => b - a);
  return entries[0]?.[0] ?? null;
}

function formatDate(iso: string | null): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString();
}

export default function RepositoriesPage() {
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const { data: repositories, isLoading, error } = useRepositories();

  return (
    <div className="flex flex-col gap-6">
      <AddRepositoryDialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} />
      <PageHeader
        title="Repositories"
        description="Manage your connected repositories"
        action={
          <Button className="gap-2" onClick={() => setAddDialogOpen(true)}>
            <Plus size={16} />
            Add Repository
          </Button>
        }
      />

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-2xl bg-muted" />
          ))}
        </div>
      )}

      {error && (
        <Card className="flex flex-col items-center gap-3 px-6 py-12 text-center">
          <RefreshCw size={32} className="text-danger" />
          <p className="text-sm text-muted-foreground">
            Failed to load repositories. Check your connection and try again.
          </p>
          <Button variant="secondary" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Card>
      )}

      {repositories && repositories.length === 0 && (
        <EmptyState
          icon={GitBranch}
          title="No repositories yet"
          description="Connect your first repository to start exploring your codebase with AI-powered search."
          action={<Button className="gap-2" onClick={() => setAddDialogOpen(true)}><Plus size={16} />Add Repository</Button>}
        />
      )}

      {repositories && repositories.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {repositories.map((repo) => (
            <Link key={repo.id} href={`${ROUTES.dashboard}/${repo.id}`}>
              <Card
                className={cn(
                  "flex h-full flex-col gap-3 p-5 transition-all duration-200",
                  "hover:border-primary/30 hover:shadow-glow",
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <GitBranch size={16} className="mt-0.5 flex-shrink-0 text-primary" />
                    <span className="font-semibold text-foreground">{repo.name}</span>
                  </div>
                  {isIndexed(repo.status) ? (
                    <span className="flex-shrink-0 rounded-full bg-success/10 px-2 py-0.5 text-[10px] font-medium text-success">
                      Indexed
                    </span>
                  ) : (
                    <span className="flex-shrink-0 rounded-full bg-warning/10 px-2 py-0.5 text-[10px] font-medium text-warning">
                      Pending
                    </span>
                  )}
                </div>

                {repo.description && (
                  <p className="line-clamp-2 text-sm text-muted-foreground">
                    {repo.description}
                  </p>
                )}

                <div className="mt-auto flex items-center gap-3 text-xs text-muted-foreground">
                  {primaryLanguage(repo.language_summary) && (
                    <span className="flex items-center gap-1">
                      <FileText size={12} />
                      {primaryLanguage(repo.language_summary)}
                    </span>
                  )}
                  {repo.last_indexed_at && (
                    <span>Updated {formatDate(repo.last_indexed_at)}</span>
                  )}
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
