import { createAdapter, type AnimeAdapter } from "@/animations/anime-adapter";

export interface SequentialRevealOptions {
  duration?: number;
  stagger?: number;
  easing?: string;
}

export interface ConnectorDrawOptions {
  duration?: number;
  stagger?: number;
  easing?: string;
}

function getPathLength(el: Element): number {
  return (el as SVGGeometryElement).getTotalLength();
}

let _adapter: AnimeAdapter | null = null;

async function getAdapter(): Promise<AnimeAdapter> {
  if (!_adapter) {
    _adapter = await createAdapter();
  }
  return _adapter;
}

export async function createSequentialReveal(
  targets: string,
  options: SequentialRevealOptions = {},
) {
  const { duration = 500, stagger: staggerVal = 120, easing = "easeOutExpo" } = options;

  const adapter = await getAdapter();

  return adapter.animate(targets, {
    opacity: [0, 1],
    scale: [0.85, 1],
    translateY: [16, 0],
    duration,
    delay: adapter.stagger(staggerVal),
    easing,
  });
}

export async function createConnectorDraw(
  targets: string,
  options: ConnectorDrawOptions = {},
) {
  const { duration = 400, stagger: staggerVal = 100, easing = "easeOutCubic" } = options;

  const adapter = await getAdapter();

  const lengths = new Map<Element, number>();
  document.querySelectorAll(targets).forEach((el) => {
    const len = getPathLength(el);
    lengths.set(el, len);
    el.setAttribute("stroke-dasharray", String(len));
    el.setAttribute("stroke-dashoffset", String(len));
  });

  return adapter.animate(targets, {
    strokeDashoffset: (el: Element) => [lengths.get(el) ?? getPathLength(el), 0],
    duration,
    delay: adapter.stagger(staggerVal),
    easing,
  });
}

export async function createPipelineTimeline(
  nodeSelector: string,
  connectorSelector: string,
  options: {
    nodeDuration?: number;
    nodeStagger?: number;
    connectorDuration?: number;
    connectorStagger?: number;
  } = {},
) {
  const {
    nodeDuration = 500,
    nodeStagger = 130,
    connectorDuration = 380,
    connectorStagger = 110,
  } = options;

  const adapter = await getAdapter();

  adapter.set(nodeSelector, { opacity: 0, scale: 0.82, translateY: 12 });

  document.querySelectorAll(connectorSelector).forEach((el) => {
    const len = getPathLength(el);
    el.setAttribute("stroke-dasharray", String(len));
    el.setAttribute("stroke-dashoffset", String(len));
  });

  const tl = adapter.createTimeline({ autoplay: false });

  tl.add(
    nodeSelector,
    {
      opacity: [0, 1],
      scale: [0.82, 1],
      translateY: [12, 0],
      duration: nodeDuration,
      delay: adapter.stagger(0, { start: nodeStagger }),
      easing: "easeOutExpo",
    },
  );

  tl.add(
    connectorSelector,
    {
      strokeDashoffset: (el: Element) => [getPathLength(el), 0],
      duration: connectorDuration,
      delay: adapter.stagger(0, { start: connectorStagger }),
      easing: "easeOutCubic",
    },
    `-=${nodeDuration * 0.4}`,
  );

  return tl;
}
