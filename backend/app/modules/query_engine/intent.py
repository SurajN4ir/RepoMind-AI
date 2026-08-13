"""Replaceable intent-detection policy for query planning."""

from typing import Protocol

from app.modules.query_engine.models import QueryIntent


class IntentDetector(Protocol):
    """Classify normalized user text without prescribing an implementation."""

    def detect(self, text: str) -> tuple[QueryIntent, float]:
        """Return the most likely intent and an explainable confidence score."""


class RuleBasedIntentDetector:
    """Deterministic initial intent detector suitable for transparent planning."""

    _RULES: tuple[tuple[QueryIntent, frozenset[str], float], ...] = (
        (QueryIntent.EXPLAIN, frozenset({"explain", "describe"}), 0.90),
        (QueryIntent.TRACE, frozenset({"trace", "flow"}), 0.92),
        (QueryIntent.GENERATE, frozenset({"generate", "create", "implement"}), 0.88),
        (QueryIntent.REFACTOR, frozenset({"refactor", "improve"}), 0.90),
        (QueryIntent.SEARCH_DOCUMENTATION, frozenset({"readme", "docs", "documentation"}), 0.92),
        (QueryIntent.SEARCH_ARCHITECTURE, frozenset({"architecture", "diagram"}), 0.90),
        (
            QueryIntent.SEARCH_CONFIGURATION,
            frozenset({"config", "configuration", "settings", "env"}),
            0.88,
        ),
        (
            QueryIntent.SEARCH_SYMBOL,
            frozenset({"class", "function", "method", "symbol", "interface", "middleware"}),
            0.86,
        ),
        (QueryIntent.SEARCH_FILE, frozenset({"file", "path", "directory", "folder"}), 0.84),
    )

    _PHRASE_RULES: tuple[tuple[QueryIntent, tuple[str, ...], float], ...] = (
        (QueryIntent.EXPLAIN, ("what does", "how does"), 0.92),
        (QueryIntent.TRACE, ("call path", "execution path"), 0.94),
        (QueryIntent.GENERATE, ("add new",), 0.86),
        (
            QueryIntent.GENERATE,
            ("like the existing", "similar to", "following the pattern"),
            0.88,
        ),
        (QueryIntent.GENERATE, ("write tests", "unit test", "endpoint", "new route"), 0.86),
        (QueryIntent.REFACTOR, ("code smell", "clean up"), 0.92),
        (QueryIntent.SEARCH_ARCHITECTURE, ("how is", "what is the structure"), 0.88),
    )

    def detect(self, text: str) -> tuple[QueryIntent, float]:
        """Match deterministic keywords and phrases, defaulting to code search."""
        words = set(text.casefold().replace("/", " ").replace("-", " ").split())
        for intent, keywords, confidence in self._RULES:
            if words.intersection(keywords):
                return intent, confidence

        lower = text.casefold()
        for intent, phrases, confidence in self._PHRASE_RULES:
            if any(phrase in lower for phrase in phrases):
                return intent, confidence

        return QueryIntent.SEARCH_CODE, 0.60
