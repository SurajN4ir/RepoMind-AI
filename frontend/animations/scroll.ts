/**
 * animations/scroll.ts
 *
 * Reusable scroll-based hooks for triggering animations when elements
 * enter the viewport. Built on native IntersectionObserver — no extra
 * runtime dependencies.
 */

"use client";

import { useEffect, useRef, useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface UseInViewOptions {
  /** Root margin passed to IntersectionObserver. Default: "0px 0px -80px 0px" */
  rootMargin?: string;
  /** Intersection threshold (0–1). Default: 0.15 */
  threshold?: number;
  /** If true, the observer disconnects after the first intersection. Default: true */
  once?: boolean;
}

// ---------------------------------------------------------------------------
// useInView
// ---------------------------------------------------------------------------

/**
 * Returns a [ref, isInView] tuple. Attach `ref` to any DOM element;
 * `isInView` becomes true when the element enters the viewport.
 *
 * @example
 * const [ref, isInView] = useInView();
 * return <section ref={ref}>{isInView && <Content />}</section>;
 */
export function useInView<T extends Element = HTMLDivElement>(
  options: UseInViewOptions = {},
): [React.RefObject<T | null>, boolean] {
  const { rootMargin = "0px 0px -80px 0px", threshold = 0.15, once = true } = options;

  const ref = useRef<T | null>(null);
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            if (once) observer.disconnect();
          } else if (!once) {
            setIsInView(false);
          }
        });
      },
      { rootMargin, threshold },
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [rootMargin, threshold, once]);

  return [ref, isInView];
}

// ---------------------------------------------------------------------------
// useScrollProgress
// ---------------------------------------------------------------------------

/**
 * Returns a scroll progress value (0–1) for the given element,
 * representing how far through the element the user has scrolled.
 * Useful for driving scroll-linked animations.
 */
export function useScrollProgress<T extends Element = HTMLDivElement>(): [
  React.RefObject<T | null>,
  number,
] {
  const ref = useRef<T | null>(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const handleScroll = () => {
      const rect = el.getBoundingClientRect();
      const windowH = window.innerHeight;
      const total = rect.height + windowH;
      const current = windowH - rect.top;
      setProgress(Math.min(1, Math.max(0, current / total)));
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return [ref, progress];
}

// ---------------------------------------------------------------------------
// useScrollY
// ---------------------------------------------------------------------------

/**
 * Returns the current window scroll Y position, updated on scroll.
 * Throttled via requestAnimationFrame.
 */
export function useScrollY(): number {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    let ticking = false;

    const handleScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          setScrollY(window.scrollY);
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return scrollY;
}
