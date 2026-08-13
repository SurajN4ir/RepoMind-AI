"""Deterministic, storage-agnostic formatter for repository structure context.

Aggregates file-level dependency and path data into a structured, LLM-friendly
module overview. The formatter does not access databases or stores — it consumes
plain domain models and returns deterministic text.
"""

from collections import defaultdict
from collections.abc import Sequence

from app.modules.indexing.models import FileDependencyRecord
from app.modules.retrieval.models import RetrievedContext

_MAX_MODULES = 50
_MAX_EDGES = 50


class RepositoryContextFormatter:
    """Produces structured text summarising repository module relationships.

    Groups files by parent directory, aggregates file-level dependency edges
    to module-level counts, and surfaces which modules are referenced by
    retrieved evidence.
    """

    def format(
        self,
        dependencies: Sequence[FileDependencyRecord],
        file_paths: Sequence[str],
        retrieval_results: Sequence[RetrievedContext] | None = None,
    ) -> str:
        """Return a deterministic plain-text module overview."""
        if not file_paths:
            return ""

        module_files = _group_by_module(file_paths)
        module_edges = _aggregate_edges(dependencies, module_files)

        evidence_modules: set[str] = set()
        if retrieval_results:
            for result in retrieval_results:
                for search_result in result.results:
                    fp = search_result.metadata.get("file_path")
                    if isinstance(fp, str):
                        evidence_modules.add(_get_module(fp))

        return _build_text(module_files, module_edges, evidence_modules)


def _get_module(path: str) -> str:
    idx = path.rfind("/")
    if idx == -1:
        return "(root)"
    return path[:idx]


def _group_by_module(paths: Sequence[str]) -> dict[str, list[str]]:
    modules: dict[str, list[str]] = defaultdict(list)
    for path in sorted(paths):
        modules[_get_module(path)].append(path)
    return dict(sorted(modules.items()))


def _aggregate_edges(
    dependencies: Sequence[FileDependencyRecord],
    module_files: dict[str, list[str]],
) -> dict[tuple[str, str], int]:
    edges: dict[tuple[str, str], int] = defaultdict(int)
    for dep in dependencies:
        src = _get_module(dep.source_path)
        tgt = _get_module(dep.target_path)
        if src != tgt and src in module_files and tgt in module_files:
            edges[(src, tgt)] += 1
    return dict(sorted(edges.items()))


def _build_text(
    module_files: dict[str, list[str]],
    module_edges: dict[tuple[str, str], int],
    evidence_modules: set[str],
) -> str:
    lines: list[str] = []
    lines.append("--- Repository Structure ---")

    if module_files:
        lines.append("")
        lines.append("Modules:")
        _maybe_limit(lines, module_files, _MAX_MODULES, "module")

    if module_edges:
        lines.append("")
        lines.append("Module dependencies:")
        _maybe_limit_edges(lines, module_edges, _MAX_EDGES)

    if evidence_modules:
        evidence_str = ", ".join(sorted(evidence_modules))
        lines.append("")
        lines.append(f"Evidence covers: {evidence_str}")

    lines.append("--- end structure ---")
    return "\n".join(lines)


def _maybe_limit(
    lines: list[str],
    items: dict[str, list[str]],
    max_items: int,
    label: str,
) -> None:
    all_items = list(items.items())
    total = len(all_items)
    if total > max_items:
        lines.append(f"  (showing {max_items} of {total} {label}s)")
    for module, files in all_items[:max_items]:
        lines.append(f"  {module}  {_dot_pad(module, items)} {len(files)} files")


def _dot_pad(key: str, items: dict[str, list[str]]) -> str:
    max_len = max(len(m) for m in items)
    return "." * (max_len - len(key) + 3)


def _maybe_limit_edges(
    lines: list[str],
    edges: dict[tuple[str, str], int],
    max_items: int,
) -> None:
    all_edges = list(edges.items())
    total = len(all_edges)
    if total > max_items:
        lines.append(f"  (showing {max_items} of {total} dependencies)")
    max_src_len = max(len(src) for src, _ in edges)
    for (src, tgt), count in all_edges[:max_items]:
        padding = "." * (max_src_len - len(src) + 3)
        lines.append(f"  {src} {padding} -> {tgt} ({count} edge{'s' if count != 1 else ''})")
