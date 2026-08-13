"use client";

/**
 * features/landing/components/animated-background.tsx
 *
 * Subtle animated background layer for the landing page.
 *
 * Renders:
 * 1. Dot grid (CSS background-image)
 * 2. Three slow-drifting gradient orbs (Framer Motion)
 * 3. Cursor-reactive radial spotlight (mouse event → CSS custom property)
 *
 * All elements are aria-hidden and pointer-events-none.
 * Orbs are disabled under prefers-reduced-motion.
 */

import { motion, useReducedMotion } from "motion/react";
import { useEffect } from "react";

// ---------------------------------------------------------------------------
// Orb definitions
// ---------------------------------------------------------------------------

interface OrbConfig {
  className: string;
  animate: Record<string, string | number | (string | number)[]>;
  duration: number;
}

const ORBS: OrbConfig[] = [
  {
    className:
      "absolute -top-40 -left-40 h-[600px] w-[600px] rounded-full bg-primary/8 blur-[120px]",
    animate: {
      x: [0, 40, -20, 0],
      y: [0, -30, 20, 0],
      scale: [1, 1.08, 0.96, 1],
    },
    duration: 28,
  },
  {
    className:
      "absolute top-1/3 -right-60 h-[700px] w-[700px] rounded-full bg-accent/6 blur-[140px]",
    animate: {
      x: [0, -50, 30, 0],
      y: [0, 40, -25, 0],
      scale: [1, 0.94, 1.06, 1],
    },
    duration: 36,
  },
  {
    className:
      "absolute -bottom-60 left-1/3 h-[500px] w-[500px] rounded-full bg-success/5 blur-[100px]",
    animate: {
      x: [0, 30, -40, 0],
      y: [0, -20, 35, 0],
      scale: [1, 1.05, 0.98, 1],
    },
    duration: 22,
  },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function AnimatedBackground() {
  const prefersReduced = useReducedMotion();

  // Cursor spotlight via CSS custom properties
  useEffect(() => {
    if (prefersReduced) return;

    const handleMouseMove = (e: MouseEvent) => {
      requestAnimationFrame(() => {
        document.documentElement.style.setProperty("--cursor-x", `${e.clientX}px`);
        document.documentElement.style.setProperty("--cursor-y", `${e.clientY}px`);
      });
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [prefersReduced]);

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
    >
      {/* Dot grid */}
      <div className="absolute inset-0 bg-grid opacity-40" />

      {/* Cursor spotlight */}
      {!prefersReduced && <div className="absolute inset-0 cursor-spotlight" />}

      {/* Gradient orbs */}
      {ORBS.map((orb, i) =>
        prefersReduced ? (
          <div key={i} className={orb.className} />
        ) : (
          <motion.div
            key={i}
            className={orb.className}
            animate={orb.animate}
            transition={{
              duration: orb.duration,
              repeat: Infinity,
              repeatType: "loop",
              ease: "easeInOut",
            }}
          />
        ),
      )}

      {/* Top vignette */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border to-transparent opacity-60" />
    </div>
  );
}
