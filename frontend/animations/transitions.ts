/**
 * animations/transitions.ts
 *
 * Page-level and component-level transition presets for Framer Motion.
 * Provides both `AnimatePresence` variants and layout transition configs.
 */

import type { Transition, Variants } from "motion/react";

// ---------------------------------------------------------------------------
// Shared easing
// ---------------------------------------------------------------------------

export const ease = [0.22, 1, 0.36, 1] as const;
export const easeIn = [0.4, 0, 1, 1] as const;
export const easeOut = [0, 0, 0.2, 1] as const;

// ---------------------------------------------------------------------------
// Page transitions
// ---------------------------------------------------------------------------

/** Fade between pages — subtle and clean. */
export const pageFade: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.3, ease } },
  exit: { opacity: 0, transition: { duration: 0.2, ease: easeIn } },
};

/** Slide up on enter, fade out on exit. */
export const pageSlideUp: Variants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.25, ease: easeIn } },
};

// ---------------------------------------------------------------------------
// Section entry transitions
// ---------------------------------------------------------------------------

/** Framer Motion transition config for section `whileInView` usage. */
export const sectionTransition: Transition = {
  duration: 0.55,
  ease,
};

/** Viewport config for `whileInView` — fires once at 15% threshold. */
export const sectionViewport = {
  once: true,
  amount: 0.15,
} as const;

// ---------------------------------------------------------------------------
// Spring presets
// ---------------------------------------------------------------------------

export const springSnappy: Transition = {
  type: "spring",
  stiffness: 400,
  damping: 30,
};

export const springGentle: Transition = {
  type: "spring",
  stiffness: 180,
  damping: 22,
};

export const springBouncy: Transition = {
  type: "spring",
  stiffness: 500,
  damping: 20,
};

// ---------------------------------------------------------------------------
// Tooltip / popover
// ---------------------------------------------------------------------------

export const tooltipVariants: Variants = {
  hidden: { opacity: 0, scale: 0.94, y: 4 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: 0.18, ease },
  },
  exit: {
    opacity: 0,
    scale: 0.94,
    y: 4,
    transition: { duration: 0.12, ease: easeIn },
  },
};

// ---------------------------------------------------------------------------
// Modal / overlay
// ---------------------------------------------------------------------------

export const overlayVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.22 } },
  exit: { opacity: 0, transition: { duration: 0.18 } },
};

export const modalVariants: Variants = {
  hidden: { opacity: 0, scale: 0.95, y: 12 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: 0.28, ease },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 8,
    transition: { duration: 0.18, ease: easeIn },
  },
};
