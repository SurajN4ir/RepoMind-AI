"use client";

import { cva, type VariantProps } from "class-variance-authority";
import { motion } from "motion/react";
import type { ComponentPropsWithoutRef } from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "focus-ring inline-flex h-10 items-center justify-center rounded-xl px-4 text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-primary text-slate-950 hover:bg-primary/90",
        secondary: "bg-card text-foreground hover:bg-muted",
        ghost: "text-muted-foreground hover:bg-muted hover:text-foreground",
      },
    },
    defaultVariants: { variant: "primary" },
  },
);

type ButtonProps = ComponentPropsWithoutRef<typeof motion.button> & VariantProps<typeof buttonVariants>;

export function Button({ className, variant, ...props }: ButtonProps) {
  return (
    <motion.button
      className={cn(buttonVariants({ variant, className }))}
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.16 }}
      {...props}
    />
  );
}
