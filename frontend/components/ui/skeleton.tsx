import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type SkeletonProps = HTMLAttributes<HTMLDivElement> & {
  variant?: "text" | "circular" | "rectangular";
};

export function Skeleton({ className, variant = "text", ...props }: SkeletonProps) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        "animate-pulse bg-muted",
        variant === "circular" && "rounded-full",
        variant === "text" && "h-4 w-full rounded-md",
        variant === "rectangular" && "rounded-xl",
        className,
      )}
      {...props}
    />
  );
}
