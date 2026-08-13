export interface GraphNode {
  id: string;
  label: string;
  type: "file" | "directory" | "module";
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface ModuleInfo {
  name: string;
  fileCount: number;
  inbound: number;
  outbound: number;
  files: string[];
}

function findCommonPrefix(paths: string[]): string {
  if (paths.length === 0) return "";
  const segments = paths.map((p) => p.split("/"));
  const minLen = Math.min(...segments.map((s) => s.length));
  const common: string[] = [];
  for (let i = 0; i < minLen; i++) {
    const candidate = segments[0][i];
    if (segments.every((s) => s[i] === candidate)) {
      common.push(candidate);
    } else {
      break;
    }
  }
  return common.length > 0 ? common.join("/") + "/" : "";
}

export function extractModuleName(filePath: string, prefix: string): string {
  const stripped = filePath.startsWith(prefix)
    ? filePath.slice(prefix.length)
    : filePath;
  const parts = stripped.split("/");
  return parts[0] || "other";
}

export function aggregateToModules(
  nodes: GraphNode[],
  edges: GraphEdge[],
): { nodes: GraphNode[]; edges: GraphEdge[]; modules: Map<string, ModuleInfo> } {
  const fileNodes = nodes.filter((n) => n.type === "file");
  const filePaths = fileNodes.map((n) => n.id);
  const prefix = findCommonPrefix(filePaths);

  const nodeToModule = new Map<string, string>();
  const moduleFiles = new Map<string, string[]>();

  for (const node of fileNodes) {
    const mod = extractModuleName(node.id, prefix);
    nodeToModule.set(node.id, mod);
    const files = moduleFiles.get(mod) ?? [];
    files.push(node.id);
    moduleFiles.set(mod, files);
  }

  const moduleSet = new Set(moduleFiles.keys());

  const moduleEdgeMap = new Map<string, Set<string>>();
  const reverseEdgeMap = new Map<string, Set<string>>();

  for (const edge of edges) {
    const srcMod = nodeToModule.get(edge.source);
    const tgtMod = nodeToModule.get(edge.target);
    if (srcMod && tgtMod && srcMod !== tgtMod && moduleSet.has(srcMod) && moduleSet.has(tgtMod)) {
      if (!moduleEdgeMap.has(srcMod)) moduleEdgeMap.set(srcMod, new Set());
      moduleEdgeMap.get(srcMod)!.add(tgtMod);
      if (!reverseEdgeMap.has(tgtMod)) reverseEdgeMap.set(tgtMod, new Set());
      reverseEdgeMap.get(tgtMod)!.add(srcMod);
    }
  }

  const moduleNodes: GraphNode[] = [];
  const moduleEdges: GraphEdge[] = [];
  const modules = new Map<string, ModuleInfo>();

  for (const [mod, files] of moduleFiles) {
    const outbound = moduleEdgeMap.get(mod)?.size ?? 0;
    const inbound = reverseEdgeMap.get(mod)?.size ?? 0;
    modules.set(mod, { name: mod, fileCount: files.length, inbound, outbound, files });
    moduleNodes.push({ id: mod, label: mod, type: "module" });
  }

  for (const [src, targets] of moduleEdgeMap) {
    for (const tgt of targets) {
      moduleEdges.push({ source: src, target: tgt });
    }
  }

  return { nodes: moduleNodes, edges: moduleEdges, modules };
}
