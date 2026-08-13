/**
 * animations/anime-adapter.ts
 *
 * Minimal typed wrapper around animejs (v4).
 *
 * Why?
 * - Avoids repeated `import("animejs")` dynamic imports across consumers
 * - Avoids pervasive `as any` casts that were needed when consuming
 *   animejs types directly
 * - Provides a stable interface that could be swapped for a different
 *   runtime (e.g. WAAPI) without changing consumer code
 *
 * Usage:
 * ```ts
 * import { createAdapter } from "@/animations/anime-adapter";
 *
 * const adapter = await createAdapter();
 * adapter.set(".el", { opacity: 0 });
 * const tl = adapter.createTimeline({ autoplay: false });
 * tl.add(".el", { opacity: [0, 1], duration: 400 });
 * tl.play();
 * ```
 */

// ---------------------------------------------------------------------------
// Public types returned by the adapter so consumers don't need animejs types
// ---------------------------------------------------------------------------

export interface AdapterTimeline {
  add(
    targets: string,
    params: Record<string, unknown>,
    position?: string | number,
  ): AdapterTimeline;
  set(
    targets: string,
    params: Record<string, unknown>,
  ): AdapterTimeline;
  play(): void;
  pause(): void;
}

export interface AnimeAdapter {
  set: (targets: string, params: Record<string, unknown>) => void;
  stagger: (val: number | string, params?: Record<string, unknown>) => unknown;
  animate: (
    targets: string,
    params: Record<string, unknown>,
  ) => { pause: () => void };
  createTimeline: (params?: Record<string, unknown>) => AdapterTimeline;
}

// ---------------------------------------------------------------------------
// Adapter factory  (lazy-loads animejs on first call)
// ---------------------------------------------------------------------------

export async function createAdapter(): Promise<AnimeAdapter> {
  const anime = await import("animejs");

  function set(targets: string, params: Record<string, unknown>): void {
    anime.utils.set(targets as never, params as never);
  }

  function stagger(
    val: number | string,
    params?: Record<string, unknown>,
  ): unknown {
    return anime.utils.stagger(val as never, params as never);
  }

  function animate(
    targets: string,
    params: Record<string, unknown>,
  ): { pause: () => void } {
    return anime.animate(targets as never, params as never) as never;
  }

  function createTimeline(
    params?: Record<string, unknown>,
  ): AdapterTimeline {
    const tl = anime.createTimeline(params as never) as never as {
      add: (
        targets: string,
        params: Record<string, unknown>,
        position?: string | number,
      ) => typeof tl;
      set: (targets: string, params: Record<string, unknown>) => typeof tl;
      play: () => void;
      pause: () => void;
    };

    return {
      add(
        targets: string,
        animParams: Record<string, unknown>,
        position?: string | number,
      ): AdapterTimeline {
        tl.add(targets, animParams as never, position as never);
        return this;
      },
      set(targets: string, animParams: Record<string, unknown>): AdapterTimeline {
        tl.set(targets, animParams as never);
        return this;
      },
      play: () => tl.play(),
      pause: () => tl.pause(),
    };
  }

  return { set, stagger, animate, createTimeline };
}
