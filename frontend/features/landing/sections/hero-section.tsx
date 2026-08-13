"use client";

/**
 * features/landing/sections/hero-section.tsx
 *
 * Full-viewport hero with a staged headline animation that tells a story:
 *
 *   "Understand" → "Any" → "Repository" → "In Minutes."
 *
 * Followed by sub-headline, CTAs, and a mini stats bar.
 *
 * Animation sequence (Framer Motion, staggered word reveals):
 * - Words appear with opacity + translateY + blur filter fade
 * - Sub-headline fades in after final word
 * - CTAs slide up after sub-headline
 * - Stats bar fades in last
 *
 * All animations disabled under prefers-reduced-motion.
 */

import { motion, useReducedMotion } from "motion/react";

import Link from "next/link";
import { ArrowRightIcon, GithubIcon } from "@/components/icons/navigation-icons";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  heroHeadlineContainer,
  heroWord,
  fadeInUp,
  fadeIn,
  staggerContainer,
  staggerItem,
} from "@/animations/variants";
import {
  HERO_HEADLINE_WORDS,
  HERO_SUBHEADLINE,
  HERO_CTA_PRIMARY,
  HERO_CTA_SECONDARY,
} from "@/features/landing/constants/landing";
import { HERO_STATS } from "@/features/landing/data/comparison";
import { ROUTES } from "@/lib/constants";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function HeroSection() {
  const prefersReduced = useReducedMotion();

  return (
    <section
      id="hero"
      aria-label="Hero — RepoMind introduction"
      className="relative flex min-h-screen flex-col items-center justify-center px-6 pb-24 pt-32 text-center"
    >
      {/* Radial highlight behind headline */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-full"
      >
        <div className="absolute left-1/2 top-1/4 h-[500px] w-[800px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/5 blur-[100px]" />
      </div>

      {/* Announcement badge */}
      <motion.div
        variants={prefersReduced ? {} : fadeIn}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.1 }}
      >
        <Badge className="mb-8 cursor-default text-xs tracking-wide">
          ✦ Production-grade Repository Intelligence
        </Badge>
      </motion.div>

      {/* Headline — word-by-word reveal */}
      <motion.h1
        className="mx-auto max-w-4xl text-5xl font-bold tracking-[-0.04em] sm:text-6xl md:text-7xl lg:text-8xl"
        variants={prefersReduced ? {} : heroHeadlineContainer}
        initial="hidden"
        animate="visible"
        aria-label={HERO_HEADLINE_WORDS.join(" ")}
      >
        {HERO_HEADLINE_WORDS.map((word, i) => (
          <motion.span
            key={word}
            variants={prefersReduced ? {} : heroWord}
            className={
              i === HERO_HEADLINE_WORDS.length - 1
                ? "text-gradient ml-0 block sm:inline"
                : "mr-[0.25em] inline-block"
            }
          >
            {word}
          </motion.span>
        ))}
      </motion.h1>

      {/* Sub-headline */}
      <motion.p
        className="mx-auto mt-8 max-w-2xl text-base leading-relaxed text-muted-foreground sm:text-lg"
        variants={prefersReduced ? {} : fadeInUp}
        initial="hidden"
        animate="visible"
        transition={{ delay: prefersReduced ? 0 : 1.1 }}
      >
        {HERO_SUBHEADLINE}
      </motion.p>

      {/* CTA buttons */}
      <motion.div
        className="mt-10 flex flex-wrap justify-center gap-4"
        variants={prefersReduced ? {} : fadeInUp}
        initial="hidden"
        animate="visible"
        transition={{ delay: prefersReduced ? 0 : 1.35 }}
      >
        <Link href={ROUTES.signUp}>
          <Button
            variant="primary"
            className="h-12 gap-2 px-6 text-sm font-semibold shadow-glow"
            aria-label={`${HERO_CTA_PRIMARY} — navigate to sign-up`}
          >
            {HERO_CTA_PRIMARY}
            <ArrowRightIcon size={16} aria-hidden="true" />
          </Button>
        </Link>

        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="focus-ring inline-flex h-12 items-center gap-2 rounded-xl border border-border bg-surface/60 px-6 text-sm font-medium text-muted-foreground backdrop-blur-sm transition-colors hover:border-border/80 hover:text-foreground"
          aria-label={`${HERO_CTA_SECONDARY} (opens in new tab)`}
        >
          <GithubIcon size={16} aria-hidden="true" />
          {HERO_CTA_SECONDARY}
        </a>
      </motion.div>

      {/* Stats bar */}
      <motion.div
        className="mt-20 w-full max-w-2xl"
        variants={prefersReduced ? {} : staggerContainer}
        initial="hidden"
        animate="visible"
        transition={{ delayChildren: prefersReduced ? 0 : 1.6 }}
      >
        <div className="grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-border bg-border sm:grid-cols-4">
          {HERO_STATS.map((stat) => (
            <motion.div
              key={stat.label}
              className="flex flex-col items-center justify-center bg-surface/80 px-4 py-5 backdrop-blur-sm"
              variants={prefersReduced ? {} : staggerItem}
            >
              <span className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                {stat.value}
              </span>
              <span className="mt-1 text-center text-xs text-muted-foreground">
                {stat.label}
              </span>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Scroll indicator */}
      {!prefersReduced && (
        <motion.div
          className="absolute bottom-10 left-1/2 -translate-x-1/2"
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.2, duration: 0.5 }}
          aria-hidden="true"
        >
          <motion.div
            className="flex h-10 w-6 items-start justify-center rounded-full border border-border/60 p-1.5"
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <motion.div
              className="h-2 w-1 rounded-full bg-muted-foreground"
              animate={{ y: [0, 8, 0] }}
              transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
            />
          </motion.div>
        </motion.div>
      )}
    </section>
  );
}
