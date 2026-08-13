"""Language detection for supported repository source files."""

from enum import StrEnum
from pathlib import Path


class SupportedLanguage(StrEnum):
    """Languages supported by the semantic parser."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"


class LanguageDetector:
    """Map file extensions to language-agnostic parser language identifiers."""

    _EXTENSIONS: dict[str, SupportedLanguage] = {
        ".py": SupportedLanguage.PYTHON,
        ".js": SupportedLanguage.JAVASCRIPT,
        ".jsx": SupportedLanguage.JAVASCRIPT,
        ".ts": SupportedLanguage.TYPESCRIPT,
        ".tsx": SupportedLanguage.TYPESCRIPT,
    }

    def detect(self, path: str | Path) -> SupportedLanguage | None:
        """Return the supported language for a path, or ``None`` when unsupported."""
        return self._EXTENSIONS.get(Path(path).suffix.lower())
