"use client";

import { Highlight, themes } from "prism-react-renderer";
import { motion } from "motion/react";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface CodeViewerProps {
  code: string;
  language?: string;
  highlightLines?: [number, number];
  fileName?: string;
  isLoading?: boolean;
}

const MAX_LINES = 500;

export function CodeViewer({ code, language, highlightLines, fileName, isLoading }: CodeViewerProps) {
  const prismLang = (language ?? "python").toLowerCase();
  const lines = code.split("\n").slice(0, MAX_LINES);

  if (isLoading) {
    return (
      <Card className="overflow-hidden">
        <div className="flex items-center border-b border-border px-4 py-2">
          <div className="h-3 w-32 animate-pulse rounded bg-muted" />
        </div>
        <div className="space-y-2 p-4">
          {Array.from({ length: 15 }).map((_, i) => (
            <div
              key={i}
              className="h-4 animate-pulse rounded bg-muted"
              style={{ width: `${40 + Math.random() * 50}%`, opacity: 1 - i * 0.03 }}
            />
          ))}
        </div>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <Card className="overflow-hidden">
        {(fileName || language) && (
          <div className="flex items-center justify-between border-b border-border px-4 py-2">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              {fileName && <span className="font-mono">{fileName}</span>}
              {language && (
                <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium uppercase">
                  {language}
                </span>
              )}
            </div>
            <span className="text-[10px] text-muted-foreground">
              {lines.length} lines
            </span>
          </div>
        )}
        <div className="overflow-x-auto">
          <Highlight
            code={code.slice(0, MAX_LINES * 80)}
            language={prismLang}
            theme={themes.nightOwl}
          >
            {({ tokens, getTokenProps }) => (
              <table className="w-full border-collapse">
                <tbody>
                  {tokens.slice(0, MAX_LINES).map((lineTokens, i) => {
                    const lineNum = i + 1;
                    const isHighlighted =
                      highlightLines &&
                      lineNum >= highlightLines[0] &&
                      lineNum <= highlightLines[1];

                    return (
                      <tr
                        key={i}
                        className={cn(isHighlighted && "bg-primary/5")}
                      >
                        <td className="select-none px-4 text-right text-[11px] leading-6 text-muted-foreground/40">
                          {lineNum}
                        </td>
                        <td className="px-4 text-[13px] leading-6">
                          <code className="font-mono">
                            {lineTokens.map((token, j) => (
                              <span
                                key={j}
                                {...getTokenProps({ token, key: j })}
                              />
                            ))}
                          </code>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </Highlight>
        </div>
      </Card>
    </motion.div>
  );
}
