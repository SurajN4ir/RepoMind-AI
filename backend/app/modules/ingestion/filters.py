"""Configurable repository workspace filtering rules."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class FileFilterDecision:
    """The inclusion result for one candidate repository file."""

    include: bool
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class IngestionFilterConfig:
    """Filtering policy for generated, dependent, binary, and oversized files."""

    max_file_size_bytes: int = 1_048_576
    ignored_directories: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                ".git",
                ".cache",
                ".mypy_cache",
                ".next",
                ".pytest_cache",
                ".ruff_cache",
                ".venv",
                "__pycache__",
                "build",
                "coverage",
                "dist",
                "node_modules",
                "target",
                "venv",
            }
        )
    )
    binary_extensions: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                ".7z",
                ".avi",
                ".bin",
                ".class",
                ".dll",
                ".dylib",
                ".exe",
                ".gif",
                ".gz",
                ".ico",
                ".jar",
                ".jpeg",
                ".jpg",
                ".mp3",
                ".mp4",
                ".o",
                ".pdf",
                ".png",
                ".so",
                ".tar",
                ".wasm",
                ".webp",
                ".zip",
            }
        )
    )


class RepositoryFileFilter:
    """Apply a configurable, content-safe repository file selection policy."""

    def __init__(self, config: IngestionFilterConfig | None = None) -> None:
        self._config = config or IngestionFilterConfig()

    def should_ignore_directory(self, directory_name: str) -> bool:
        """Return whether a directory must be pruned before recursive traversal."""
        return directory_name in self._config.ignored_directories

    def evaluate(self, path: Path, size_bytes: int) -> FileFilterDecision:
        """Evaluate non-content file rules before reading a candidate file."""
        if size_bytes > self._config.max_file_size_bytes:
            return FileFilterDecision(include=False, reason="oversized")
        if path.suffix.lower() in self._config.binary_extensions:
            return FileFilterDecision(include=False, reason="binary")
        return FileFilterDecision(include=True)

    @staticmethod
    def is_binary_file(path: Path) -> bool:
        """Use a small NUL-byte probe to exclude binary files without retaining content."""
        with path.open("rb") as file_handle:
            return b"\x00" in file_handle.read(8_192)
