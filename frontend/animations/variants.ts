/**
 * animations/variants.ts
 *
 * Centralised Framer Motion variant definitions for RepoMind.
 * Import these rather than writing ad-hoc `initial`/`animate` objects
 * in individual components.
 *
 * All variants respect `prefers-reduced-motion` via the `useReducedMotion`
 * hook from Framer Motion — pass `shouldReduce` at the call site to
 * conditionally return identity (no-op) variants.
 */

import type { Variants } from "motion/react";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Identity variants — used when reduced motion is preferred. */
export const identityVariants: Variants = {
  hidden: {},
  visible: {},
};

/**
 * Returns the given variant set unchanged, or identity variants when the
 * user prefers reduced motion.
 */
export function withReducedMotion(
  variants: Variants,
  prefersReduced: boolean,
): Variants {
  return prefersReduced ? identityVariants : variants;
}

// ---------------------------------------------------------------------------
// Fade
// ---------------------------------------------------------------------------

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
};

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } },
};

export const fadeInDown: Variants = {
  hidden: { opacity: 0, y: -20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] } },
};

// ---------------------------------------------------------------------------
// Slide
// ---------------------------------------------------------------------------

export const slideInLeft: Variants = {
  hidden: { opacity: 0, x: -32 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } },
};

export const slideInRight: Variants = {
  hidden: { opacity: 0, x: 32 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } },
};

// ---------------------------------------------------------------------------
// Scale
// ---------------------------------------------------------------------------

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.92 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
};

// ---------------------------------------------------------------------------
// Stagger containers
// ---------------------------------------------------------------------------

/** Wrap a list of `staggerItem` children to get an auto-staggered reveal. */
export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
};

/** Stagger with a slightly larger gap — for coarser grids. */
export const staggerContainerSlow: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.14,
      delayChildren: 0.12,
    },
  },
};

/** Child of `staggerContainer` — slides up and fades in. */
export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] },
  },
};

// ---------------------------------------------------------------------------
// Hero word-by-word
// ---------------------------------------------------------------------------

/** Container that staggers individual word spans for the hero headline. */
export const heroHeadlineContainer: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2,
    },
  },
};

/** Each word in the hero headline. */
export const heroWord: Variants = {
  hidden: { opacity: 0, y: 32, filter: "blur(8px)" },
  visible: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] },
  },
};

// ---------------------------------------------------------------------------
// Cards / interactive elements
// ---------------------------------------------------------------------------

export const cardHover: Variants = {
  rest: { scale: 1, y: 0 },
  hover: { scale: 1.015, y: -3, transition: { duration: 0.22, ease: [0.22, 1, 0.36, 1] } },
};

export const iconHover: Variants = {
  rest: { scale: 1, rotate: 0 },
  hover: { scale: 1.15, rotate: 6, transition: { duration: 0.2, ease: "easeOut" } },
};

// ---------------------------------------------------------------------------
// Nav
// ---------------------------------------------------------------------------

export const navItem: Variants = {
  hidden: { opacity: 0, y: -8 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] } },
};

export const navContainer: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.06, delayChildren: 0.1 } },
};
