"use client";

import Image from "next/image";

import { cn } from "@/lib/utils";

type AvatarProps = {
  initials: string;
  className?: string;
  src?: string;
  alt?: string;
};

export function Avatar({ initials, className, src, alt }: AvatarProps) {
  if (src) {
    return (
      <Image
        src={src}
        alt={alt ?? "User avatar"}
        width={32}
        height={32}
        className={cn("h-8 w-8 rounded-full object-cover", className)}
      />
    );
  }

  return (
    <div
      className={cn(
        "flex h-8 w-8 items-center justify-center rounded-full bg-primary/20 text-xs font-semibold text-primary",
        className,
      )}
      aria-label={alt ?? `Avatar: ${initials}`}
    >
      {initials}
    </div>
  );
}
