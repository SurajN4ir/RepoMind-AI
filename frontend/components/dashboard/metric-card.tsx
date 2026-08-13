"use client";

import type { ReactNode } from "react";
import { motion } from "motion/react";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  trend?: { direction: "up" | "down" | "neutral"; label: string };
  isLoading?: boolean;
}

export function MetricCard({ label, value, icon, trend, isLoading }: MetricCardProps) {
  if (isLoading) {
    return (
      <Card className="p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="h-3 w-20 animate-pulse rounded bg-muted" />
            <div className="h-8 w-16 animate-pulse rounded bg-muted" />
          </div>
          <div className="h-10 w-10 animate-pulse rounded-xl bg-muted" />
        </div>
        {trend && <div className="mt-3 h-3 w-24 animate-pulse rounded bg-muted" />}
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="relative p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground">{label}</p>
            <p className="text-2xl font-semibold tracking-tight text-foreground">
              {value}
            </p>
          </div>
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
            {icon}
          </div>
        </div>
        {trend && (
          <div className="mt-3 flex items-center gap-1.5">
            <span
              className={cn(
                "inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium",
                trend.direction === "up" && "bg-success/10 text-success",
                trend.direction === "down" && "bg-destructive/10 text-destructive",
                trend.direction === "neutral" && "bg-muted text-muted-foreground",
              )}
            >
              {trend.label}
            </span>
          </div>
        )}
      </Card>
    </motion.div>
  );
}
