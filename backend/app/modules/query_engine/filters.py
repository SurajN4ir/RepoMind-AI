"""Pure extraction of supported metadata filters from user language."""

import re
from collections.abc import Mapping


class MetadataFilterExtractor:
    """Extract a small, explicit set of retrieval metadata filters."""

    _LANGUAGES = frozenset({"python", "javascript", "typescript"})
    _PATH_PATTERN = re.compile(
        r"\b(?:inside|under|in)\s+(?:the\s+)?([A-Za-z0-9_./-]+)\s+(?:folder|directory)\b",
        re.IGNORECASE,
    )
    _EXPLICIT_PATH_PATTERN = re.compile(r"\bpath\s*:\s*([A-Za-z0-9_./-]+)", re.IGNORECASE)

    def extract(self, text: str) -> Mapping[str, object]:
        """Return provider-neutral metadata filters without rewriting the query text."""
        filters: dict[str, object] = {}
        words = set(text.casefold().replace("-", " ").split())
        language = next((item for item in self._LANGUAGES if item in words), None)
        if language is not None:
            filters["language"] = language
        path_match = self._EXPLICIT_PATH_PATTERN.search(text) or self._PATH_PATTERN.search(text)
        if path_match is not None:
            filters["file_path_prefix"] = path_match.group(1).rstrip("/") + "/"
        return filters
