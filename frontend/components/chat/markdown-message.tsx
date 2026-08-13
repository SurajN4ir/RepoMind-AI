"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Highlight, themes } from "prism-react-renderer";
import type { ComponentProps } from "react";

import { resolvePrismLanguage } from "@/lib/prism-language-map";

interface MarkdownMessageProps {
  content: string;
}

function CodeBlock({ className, children }: { className?: string; children?: React.ReactNode }) {
  const language = className?.replace("language-", "") ?? "";
  const code = String(children ?? "").replace(/\n$/, "");

  if (!language) {
    return (
      <code className="rounded bg-muted px-1.5 py-0.5 text-sm font-mono text-foreground">
        {code}
      </code>
    );
  }

  return (
    <div className="my-3 overflow-hidden rounded-xl border border-border">
      <div className="flex items-center justify-between border-b border-border bg-muted/50 px-4 py-1.5">
        <span className="text-[10px] font-medium uppercase text-muted-foreground">
          {language}
        </span>
      </div>
      <Highlight
        code={code}
        language={resolvePrismLanguage(language)}
        theme={themes.nightOwl}
      >
        {({ tokens, getLineProps, getTokenProps }) => (
          <pre className="overflow-x-auto p-4 text-sm leading-relaxed">
            <code>
              {tokens.map((lineTokens, i) => {
                const lineProps = getLineProps({ line: lineTokens, key: i });
                return (
                  <div key={i} {...lineProps} style={undefined}>
                    {lineTokens.map((token, j) => (
                      <span key={j} {...getTokenProps({ token, key: j })} />
                    ))}
                  </div>
                );
              })}
            </code>
          </pre>
        )}
      </Highlight>
    </div>
  );
}

const components: ComponentProps<typeof ReactMarkdown>["components"] = {
  code: CodeBlock,
  pre: ({ children }) => <>{children}</>,
  a: ({ href, children, ...props }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-primary underline underline-offset-2 hover:text-primary/80"
      {...props}
    >
      {children}
    </a>
  ),
  p: ({ children, ...props }) => (
    <p className="mb-3 last:mb-0 leading-relaxed" {...props}>
      {children}
    </p>
  ),
  ul: ({ children, ...props }) => (
    <ul className="mb-3 list-disc pl-5 space-y-1" {...props}>
      {children}
    </ul>
  ),
  ol: ({ children, ...props }) => (
    <ol className="mb-3 list-decimal pl-5 space-y-1" {...props}>
      {children}
    </ol>
  ),
  h1: ({ children, ...props }) => (
    <h1 className="mb-2 mt-4 text-lg font-semibold" {...props}>
      {children}
    </h1>
  ),
  h2: ({ children, ...props }) => (
    <h2 className="mb-2 mt-3 text-base font-semibold" {...props}>
      {children}
    </h2>
  ),
  h3: ({ children, ...props }) => (
    <h3 className="mb-1 mt-2 text-sm font-semibold" {...props}>
      {children}
    </h3>
  ),
  blockquote: ({ children, ...props }) => (
    <blockquote className="mb-3 border-l-2 border-primary/30 pl-4 italic text-muted-foreground" {...props}>
      {children}
    </blockquote>
  ),
  hr: () => <hr className="my-4 border-border" />,
  table: ({ children, ...props }) => (
    <div className="mb-3 overflow-x-auto">
      <table className="w-full border-collapse text-sm" {...props}>
        {children}
      </table>
    </div>
  ),
  th: ({ children, ...props }) => (
    <th className="border border-border bg-muted px-3 py-1.5 text-left font-medium" {...props}>
      {children}
    </th>
  ),
  td: ({ children, ...props }) => (
    <td className="border border-border px-3 py-1.5" {...props}>
      {children}
    </td>
  ),
};

export function MarkdownMessage({ content }: MarkdownMessageProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={components}
    >
      {content}
    </ReactMarkdown>
  );
}
