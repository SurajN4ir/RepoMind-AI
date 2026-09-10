"use client";

import Link from "next/link";
import { Search } from "lucide-react";

import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { ROUTES } from "@/lib/constants";

/**
 * The backend's /api/search endpoint only scans a single repository's
 * indexed files and returns an empty list when called without a
 * repository_id (see backend/app/api/v1/routes/search.py) -- there is no
 * cross-repository search implemented server-side. Rather than run a query
 * that is structurally guaranteed to return nothing and claim "no results
 * found", this page is honest that global search isn't available yet and
 * points to per-repository search instead.
 */
export default function GlobalSearchPage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Semantic Search"
        description="Search across all your repositories"
      />

      <Card className="flex flex-col items-center gap-3 px-6 py-16 text-center">
        <Search size={40} className="text-muted-foreground" />
        <p className="text-sm text-muted-foreground">
          Search across all repositories at once isn&rsquo;t available yet.
          Open a repository and use its Search tab to search within it.
        </p>
        <Link
          href={ROUTES.dashboard}
          className="focus-ring mt-2 inline-flex h-10 items-center rounded-lg border border-border px-4 text-sm text-foreground hover:bg-muted"
        >
          Go to repositories
        </Link>
      </Card>
    </div>
  );
}
