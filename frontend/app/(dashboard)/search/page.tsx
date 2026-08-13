"use client";

import { useState } from "react";
import { Search } from "lucide-react";

import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SearchResultCard } from "@/components/shared/search-result-card";
import { useSearch } from "@/hooks/use-search";

export default function GlobalSearchPage() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState<string | null>(null);

  const searchParams = submittedQuery ? { q: submittedQuery } : null;
  const { data: results, isLoading } = useSearch(searchParams);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSubmittedQuery(query.trim());
  };

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Semantic Search"
        description="Search across all your repositories"
      />

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search size={16} className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search across all repositories..."
            className="focus-ring h-12 w-full rounded-xl border border-border bg-surface pl-11 pr-4 text-sm text-foreground placeholder:text-muted-foreground/60"
          />
        </div>
        <Button type="submit" disabled={!query.trim() || isLoading}>
          {isLoading ? "Searching..." : "Search"}
        </Button>
      </form>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-muted" />
          ))}
        </div>
      )}

      {results && results.length === 0 && submittedQuery && (
        <Card className="flex flex-col items-center gap-3 px-6 py-12 text-center">
          <Search size={32} className="text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            No results found for &ldquo;{submittedQuery}&rdquo;.
          </p>
        </Card>
      )}

      {results && results.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground">
            {results.length} result{results.length !== 1 ? "s" : ""}
          </p>
          {results.map((result, i) => (
            <SearchResultCard key={i} result={result} showRepository />
          ))}
        </div>
      )}

      {!submittedQuery && (
        <Card className="flex flex-col items-center gap-3 px-6 py-16 text-center">
          <Search size={40} className="text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            Search across all your indexed repositories simultaneously.
          </p>
        </Card>
      )}
    </div>
  );
}
