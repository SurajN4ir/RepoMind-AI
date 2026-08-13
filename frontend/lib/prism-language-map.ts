const prismLanguageMap: Record<string, string> = {
  TypeScript: "tsx",
  JavaScript: "jsx",
  Python: "python",
  "C++": "cpp",
  "C#": "csharp",
  "C": "c",
  Go: "go",
  Rust: "rust",
  Java: "java",
  Kotlin: "kotlin",
  Swift: "swift",
  Ruby: "ruby",
  PHP: "php",
  Shell: "bash",
  Bash: "bash",
  Dockerfile: "docker",
  YAML: "yaml",
  yaml: "yaml",
  JSON: "json",
  HTML: "html",
  CSS: "css",
  SCSS: "scss",
  SQL: "sql",
  GraphQL: "graphql",
  Markdown: "markdown",
  MDX: "mdx",
  Plain: "plaintext",
  Text: "plaintext",
  Diff: "diff",
};

export function resolvePrismLanguage(language: string | null | undefined): string {
  if (!language) return "python";
  const normalized = language.trim();
  return prismLanguageMap[normalized] ?? normalized.toLowerCase();
}
