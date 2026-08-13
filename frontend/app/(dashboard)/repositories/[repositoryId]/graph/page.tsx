"use client";

import { useParams } from "next/navigation";
import { useState } from "react";

import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { DependencyGraph } from "@/components/code/dependency-graph";
import { useGraphData } from "@/hooks/use-graph-data";
import { useRepository } from "@/hooks/use-repositories";

export default function RepositoryGraphPage() {
  const params = useParams();
  const repoId = params.repositoryId as string;
  const { data: repo } = useRepository(repoId);
  const { data: graphData, isLoading } = useGraphData(repoId);
  const [viewMode, setViewMode] = useState<"file" | "module">("file");

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={`Graph — ${repo?.name ?? "Repository"}`}
        description="Visualize code dependencies and module relationships"
      />
      <Card className="p-5">
        <DependencyGraph
          nodes={graphData?.nodes ?? []}
          edges={graphData?.edges ?? []}
          isLoading={isLoading}
          repositoryId={repoId}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
        />
      </Card>
    </div>
  );
}
