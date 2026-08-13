"""Unit tests for the RepositoryContextFormatter."""

from uuid import uuid4

from app.modules.indexing.models import FileDependencyRecord
from app.modules.insight.repository_context_formatter import (
    RepositoryContextFormatter,
)


class TestRepositoryContextFormatter:
    """Tests for the deterministic structure formatter."""

    def test_empty_paths_returns_empty_string(self) -> None:
        formatter = RepositoryContextFormatter()
        result = formatter.format(dependencies=[], file_paths=[])
        assert result == ""

    def test_single_module(self) -> None:
        formatter = RepositoryContextFormatter()
        paths = ["src/auth.py", "src/main.py"]
        result = formatter.format(dependencies=[], file_paths=paths)
        assert "src" in result
        assert "2 files" in result

    def test_multiple_modules(self) -> None:
        formatter = RepositoryContextFormatter()
        paths = ["src/auth/login.py", "src/main.py", "tests/test_auth.py"]
        result = formatter.format(dependencies=[], file_paths=paths)
        assert "src" in result
        assert "tests" in result
        assert "1 files" in result or "2 files" in result

    def test_root_level_files(self) -> None:
        formatter = RepositoryContextFormatter()
        paths = ["README.md", "setup.py", "src/main.py"]
        result = formatter.format(dependencies=[], file_paths=paths)
        assert "(root)" in result

    def test_cross_module_edges_appear(self) -> None:
        formatter = RepositoryContextFormatter()
        paths = ["src/auth/login.py", "src/api/users.py"]
        rid = uuid4()
        dependencies = [
            FileDependencyRecord(
                repository_id=rid,
                source_path="src/api/users.py",
                target_path="src/auth/login.py",
            ),
        ]
        result = formatter.format(dependencies=dependencies, file_paths=paths)
        assert "->" in result
        assert "1 edge" in result

    def test_intra_module_edges_excluded(self) -> None:
        formatter = RepositoryContextFormatter()
        paths = ["src/auth/login.py", "src/auth/register.py"]
        rid = uuid4()
        dependencies = [
            FileDependencyRecord(
                repository_id=rid,
                source_path="src/auth/login.py",
                target_path="src/auth/register.py",
            ),
        ]
        result = formatter.format(dependencies=dependencies, file_paths=paths)
        assert "Module dependencies" in result or "--- end structure ---" in result
        assert "src/auth/login.py" not in result or "->" not in result

    def test_evidence_coverage_listed(self) -> None:
        from app.modules.retrieval.models import (
            RetrievalStatistics,
            RetrievedContext,
            SearchQuery,
            SearchResult,
        )

        formatter = RepositoryContextFormatter()
        paths = ["src/auth/login.py", "src/api/users.py", "tests/test_auth.py"]
        query = SearchQuery(text="auth")
        retrieval = RetrievedContext(
            query=query,
            results=(
                SearchResult(
                    chunk_id="c1",
                    score=0.9,
                    text="login code",
                    metadata={"file_path": "src/auth/login.py"},
                ),
            ),
            citations=(),
            statistics=RetrievalStatistics(
                vector_hits=1,
                keyword_hits=0,
                rrf_time_seconds=0.0,
                retrieval_time_seconds=0.0,
                rerank_time_seconds=0.0,
            ),
        )
        result = formatter.format(
            dependencies=[],
            file_paths=paths,
            retrieval_results=[retrieval],
        )
        assert "Evidence covers:" in result
        assert "src/auth" in result

    def test_large_repo_truncates(self) -> None:
        formatter = RepositoryContextFormatter()
        paths = [f"module_{i}/file.py" for i in range(60)]
        result = formatter.format(dependencies=[], file_paths=paths)
        assert "showing 50 of 60 modules" in result or "showing 50" in result
