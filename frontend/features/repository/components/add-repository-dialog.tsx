"use client";

import { useState, type FormEvent } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useCreateRepository } from "@/hooks/use-create-repository";
import { useToast } from "@/providers/toast-provider";

interface AddRepositoryDialogProps {
  open: boolean;
  onClose: () => void;
}

const PROVIDERS = [
  { value: "GITHUB", label: "GitHub" },
  { value: "GITLAB", label: "GitLab" },
  { value: "BITBUCKET", label: "Bitbucket" },
  { value: "LOCAL", label: "Local" },
];

export function AddRepositoryDialog({ open, onClose }: AddRepositoryDialogProps) {
  const createMutation = useCreateRepository();
  const { toast } = useToast();

  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [provider, setProvider] = useState("GITHUB");
  const [defaultBranch, setDefaultBranch] = useState("main");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  const resetForm = () => {
    setName("");
    setUrl("");
    setProvider("GITHUB");
    setDefaultBranch("main");
    setDescription("");
    setError(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Repository name is required.");
      return;
    }
    if (!url.trim()) {
      setError("Repository URL is required.");
      return;
    }
    if (!defaultBranch.trim()) {
      setError("Default branch is required.");
      return;
    }

    try {
      await createMutation.mutateAsync({
        name: name.trim(),
        url: url.trim(),
        provider,
        default_branch: defaultBranch.trim(),
        description: description.trim() || undefined,
      });
      toast(`Repository "${name.trim()}" created successfully`, "success");
      handleClose();
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to create repository. Please try again.";
      setError(message);
      toast(message, "error");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-background/60 backdrop-blur-sm"
        onClick={handleClose}
        aria-hidden="true"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Add Repository"
        className="relative w-full max-w-lg rounded-2xl border border-border bg-surface p-6 shadow-glow-lg"
      >
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-foreground">Add Repository</h2>
          <button
            type="button"
            onClick={handleClose}
            aria-label="Close dialog"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted/40 hover:text-foreground"
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          {error && (
            <div className="rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
              {error}
            </div>
          )}

          <div className="flex flex-col gap-1.5">
            <label htmlFor="repo-name" className="text-sm font-medium text-foreground">
              Repository Name <span className="text-danger">*</span>
            </label>
            <input
              id="repo-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="my-awesome-project"
              className="focus-ring rounded-xl border border-border bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground"
              required
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="repo-url" className="text-sm font-medium text-foreground">
              Repository URL <span className="text-danger">*</span>
            </label>
            <input
              id="repo-url"
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://github.com/username/repository"
              className="focus-ring rounded-xl border border-border bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground"
              required
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="repo-provider" className="text-sm font-medium text-foreground">
              Provider
            </label>
            <select
              id="repo-provider"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="focus-ring rounded-xl border border-border bg-background px-4 py-2.5 text-sm text-foreground"
            >
              {PROVIDERS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="repo-branch" className="text-sm font-medium text-foreground">
              Default Branch <span className="text-danger">*</span>
            </label>
            <input
              id="repo-branch"
              type="text"
              value={defaultBranch}
              onChange={(e) => setDefaultBranch(e.target.value)}
              placeholder="main"
              className="focus-ring rounded-xl border border-border bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground"
              required
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="repo-description" className="text-sm font-medium text-foreground">
              Description
            </label>
            <textarea
              id="repo-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description of the repository"
              rows={3}
              className="focus-ring rounded-xl border border-border bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground resize-none"
            />
          </div>

          <div className="mt-2 flex justify-end gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={handleClose}
              disabled={createMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? "Creating..." : "Create Repository"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
