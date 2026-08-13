"use client";

/**
 * features/landing/sections/cta-section.tsx
 *
 * Call to action — bold heading, subtext, two buttons.
 * Animated gradient orb background reinforces the primary call.
 */

import { motion, useReducedMotion } from "motion/react";
import Link from "next/link";
import { ArrowRightIcon, GithubIcon } from "@/components/icons/navigation-icons";
import { Button } from "@/components/ui/button";
import { SectionHeader } from "@/features/landing/components/section-header";
import { SECTION_LABELS } from "@/features/landing/constants/landing";
import { ROUTES } from "@/lib/constants";

// ---------------------------------------------------------------------------
// Section
// ---------------------------------------------------------------------------

export function CTASection() {
  const prefersReduced = useReducedMotion();

  return (
    <section
      id="cta"
      aria-labelledby="cta-heading"
      className="section-padding relative overflow-hidden"
    >
      {/* Background orb */}
      {!prefersReduced ? (
        <motion.div
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 blur-[120px]"
          animate={{
            scale: [1, 1.12, 1],
            opacity: [0.6, 0.9, 0.6],
          }}
          transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
        />
      ) : (
        <div
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 blur-[120px]"
        />
      )}

      <div className="content-width relative text-center">
        <SectionHeader
          badge="Get Started Today"
          title={SECTION_LABELS.cta}
          subtitle={SECTION_LABELS.ctaSubtitle}
          headingId="cta-heading"
          viewportAmount={0.3}
        />

        {/* Buttons */}
        <motion.div
          className="mt-10 flex flex-wrap justify-center gap-4"
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
        >
          <Link href={ROUTES.signUp}>
            <Button
              variant="primary"
              className="h-12 gap-2 px-8 text-sm font-semibold shadow-glow-lg"
              aria-label={SECTION_LABELS.ctaPrimary}
            >
              {SECTION_LABELS.ctaPrimary}
              <ArrowRightIcon size={16} aria-hidden="true" />
            </Button>
          </Link>

          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`${SECTION_LABELS.ctaSecondary} (opens in new tab)`}
            className="focus-ring inline-flex h-12 items-center gap-2 rounded-xl border border-border bg-surface/60 px-8 text-sm font-medium text-muted-foreground backdrop-blur-sm transition-colors hover:border-border/80 hover:text-foreground"
          >
            <GithubIcon size={16} aria-hidden="true" />
            {SECTION_LABELS.ctaSecondary}
          </a>
        </motion.div>
      </div>
    </section>
  );
}
