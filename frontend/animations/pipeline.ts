/**
 * animations/pipeline.ts
 *
 * Pipeline-specific animation driver.
 *
 * Orchestrates the full Repository -> AI pipeline animation using anime.js
 * through the anime-adapter wrapper.
 *
 * Usage:
 * ```ts
 * import { runPipelineAnimation } from "@/animations/pipeline";
 *
 * useEffect(() => {
 *   if (!isInView) return;
 *   const cleanup = runPipelineAnimation();
 *   return () => cleanup();
 * }, [isInView]);
 * ```
 */

import { createAdapter, type AnimeAdapter } from "@/animations/anime-adapter";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface PipelineAnimationOptions {
  /** Selector for node wrapper elements. Default: ".pipeline-node" */
  nodeSelector?: string;
  /** Selector for SVG connector lines. Default: ".pipeline-connector" */
  connectorSelector?: string;
  /** Selector for node icon elements. Default: ".pipeline-node-icon" */
  iconSelector?: string;
  /** Selector for glow/pulse elements on nodes. Default: ".pipeline-node-glow" */
  glowSelector?: string;
  /** Delay before the animation starts (ms). Default: 200 */
  startDelay?: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function setConnectorDash(
  selector: string,
): void {
  document.querySelectorAll(selector).forEach((el) => {
    const len = (el as SVGGeometryElement).getTotalLength();
    el.setAttribute("stroke-dasharray", String(len));
    el.setAttribute("stroke-dashoffset", String(len));
  });
}

// ---------------------------------------------------------------------------
// Main driver
// ---------------------------------------------------------------------------

/**
 * Runs the full pipeline animation sequence.
 * Returns a cleanup function that cancels any running animations.
 */
export function runPipelineAnimation(options: PipelineAnimationOptions = {}): () => void {
  const {
    nodeSelector = ".pipeline-node",
    connectorSelector = ".pipeline-connector",
    iconSelector = ".pipeline-node-icon",
    glowSelector = ".pipeline-node-glow",
    startDelay = 200,
  } = options;

  let cancelled = false;
  let timeline: ReturnType<AnimeAdapter["createTimeline"]> | null = null;

  (async () => {
    if (cancelled) return;

    const adapter = await createAdapter();
    if (cancelled) return;

    // --- Initial state ---
    adapter.set(nodeSelector, { opacity: 0, scale: 0.8, translateY: 10 });
    adapter.set(iconSelector, { scale: 0, rotate: -15, opacity: 0 });
    adapter.set(glowSelector, { opacity: 0, scale: 0.6 });

    // Set initial connector state & compute path lengths
    adapter.set(connectorSelector, { opacity: 0 });
    setConnectorDash(connectorSelector);

    // --- Timeline ---
    const tl = adapter.createTimeline({ autoplay: false });

    // Phase 1: Node wrappers appear
    tl.add(
      nodeSelector,
      {
        opacity: [0, 1],
        scale: [0.8, 1],
        translateY: [10, 0],
        duration: 520,
        delay: adapter.stagger(startDelay, { start: 130 }),
        easing: "easeOutExpo",
      },
    );

    // Phase 2: Icons pop in (offset from nodes)
    tl.add(
      iconSelector,
      {
        opacity: [0, 1],
        scale: [0, 1],
        rotate: [-15, 0],
        duration: 380,
        delay: adapter.stagger(0, { start: 100 }),
        easing: "easeOutBack",
      },
      `-=${520 * 0.5}`,
    );

    // Phase 3: Connectors draw
    tl.add(
      connectorSelector,
      {
        opacity: [0, 1],
        strokeDashoffset: (el: Element) => [(el as SVGGeometryElement).getTotalLength(), 0],
        duration: 400,
        delay: adapter.stagger(0, { start: 100 }),
        easing: "easeOutCubic",
      },
      `-=${380 * 0.3}`,
    );

    // Phase 4: Glow pulses
    tl.add(
      glowSelector,
      {
        opacity: [0, 0.6, 0],
        scale: [0.6, 1.4, 1],
        duration: 700,
        delay: adapter.stagger(0, { start: 120 }),
        easing: "easeOutSine",
      },
      `-=${200}`,
    );

    timeline = tl;
    if (!cancelled) tl.play();
  })();

  return () => {
    cancelled = true;
    timeline?.pause();
  };
}

// ---------------------------------------------------------------------------
// Idle pulse (runs after animation completes on the active/last node)
// ---------------------------------------------------------------------------

/**
 * Starts a continuous subtle pulse on the terminal node to indicate
 * the pipeline is "live". Returns a cancel function.
 */
export function startTerminalPulse(selector: string): () => void {
  const el = document.querySelector<HTMLElement>(selector);
  if (!el) return () => {};

  let cancelled = false;
  let instance: { pause: () => void } | null = null;

  (async () => {
    if (cancelled) return;
    const adapter = await createAdapter();
    if (cancelled) return;

    instance = adapter.animate(selector, {
      boxShadow: [
        "0 0 0px 0px hsl(218 100% 65% / 0)",
        "0 0 14px 4px hsl(218 100% 65% / 0.35)",
        "0 0 0px 0px hsl(218 100% 65% / 0)",
      ],
      duration: 2200,
      easing: "easeInOutSine",
      loop: true,
    });

    instance?.pause();
  })();

  return () => {
    cancelled = true;
    instance?.pause();
  };
}
