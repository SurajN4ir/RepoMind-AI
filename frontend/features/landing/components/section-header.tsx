"use client";

import { motion, useReducedMotion } from "motion/react";
import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { staggerContainer, staggerItem, fadeInUp } from "@/animations/variants";

type SectionHeaderProps = {
  badge?: string;
  badgeEl?: ReactNode;
  title: ReactNode;
  subtitle?: string;
  headingId?: string;
  className?: string;
  action?: ReactNode;
  viewportAmount?: number;
};

export function SectionHeader({
  badge,
  badgeEl,
  title,
  subtitle,
  headingId,
  className,
  action,
  viewportAmount = 0.2,
}: SectionHeaderProps) {
  const prefersReduced = useReducedMotion();

  return (
    <motion.div
      className={cn("mb-12 text-center", className)}
      variants={prefersReduced ? {} : staggerContainer}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: viewportAmount }}
    >
      {(badge || badgeEl) && (
        <motion.div variants={prefersReduced ? {} : staggerItem}>
          {badgeEl ?? <Badge className="mb-4">{badge}</Badge>}
        </motion.div>
      )}
      <motion.h2
        id={headingId}
        className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl"
        variants={prefersReduced ? {} : fadeInUp}
      >
        {title}
      </motion.h2>
      {subtitle && (
        <motion.p
          className="mx-auto mt-4 max-w-lg text-base text-muted-foreground"
          variants={prefersReduced ? {} : fadeInUp}
        >
          {subtitle}
        </motion.p>
      )}
      {action && (
        <motion.div variants={prefersReduced ? {} : fadeInUp}>
          {action}
        </motion.div>
      )}
    </motion.div>
  );
}
