"use client";

import { motion } from "motion/react";
import { GitCommit, GitPullRequest, FileSymlink, AlertCircle, type LucideIcon } from "lucide-react";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const defaultIcons: Record<string, LucideIcon> = {
  index_started: GitCommit,
  index_completed: GitPullRequest,
  index_failed: AlertCircle,
};

const defaultColors: Record<string, string> = {
  index_started: "bg-blue-500/10 text-blue-500",
  index_completed: "bg-purple-500/10 text-purple-500",
  index_failed: "bg-destructive/10 text-destructive",
};

interface ActivityItem {
  id: string;
  event_type: string;
  message: string;
  timestamp: string;
}

interface ActivityFeedProps {
  items: ActivityItem[];
  isLoading?: boolean;
}

export function ActivityFeed({ items, isLoading }: ActivityFeedProps) {
  if (isLoading) {
    return (
      <Card className="p-5">
        <div className="mb-4 h-4 w-28 animate-pulse rounded bg-muted" />
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex gap-3">
              <div className="h-8 w-8 flex-shrink-0 animate-pulse rounded-lg bg-muted" />
              <div className="flex-1 space-y-1.5">
                <div className="h-3 w-full animate-pulse rounded bg-muted" />
                <div className="h-3 w-2/3 animate-pulse rounded bg-muted" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
    >
      <Card className="relative p-5">
        <h3 className="mb-4 text-sm font-semibold text-foreground">Recent Activity</h3>
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No recent activity. Index this repository to see events here.
          </p>
        ) : (
          <div className="relative space-y-0">
            <div className="absolute left-[19px] top-2 h-[calc(100%-32px)] w-px bg-border" />
            {items.map((item) => {
              const Icon: LucideIcon = defaultIcons[item.event_type] ?? FileSymlink;
              return (
                <div key={item.id} className="relative flex gap-3 pb-4 last:pb-0">
                  <div
                    className={cn(
                      "relative z-10 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg",
                      defaultColors[item.event_type] ?? "bg-muted text-muted-foreground",
                    )}
                  >
                    <Icon size={14} />
                  </div>
                  <div className="flex flex-1 flex-col gap-0.5 pt-1">
                    <p className="text-sm text-foreground">{item.message}</p>
                    {item.timestamp && (
                      <p className="text-xs text-muted-foreground">{item.timestamp}</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </motion.div>
  );
}
