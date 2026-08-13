export interface SourceCitation {
  id?: string;
  filePath: string;
  lineStart: number;
  lineEnd: number;
  description?: string;
}

export function citationId(c: SourceCitation): string {
  return c.id ?? `${c.filePath}:${c.lineStart}:${c.lineEnd}`;
}
