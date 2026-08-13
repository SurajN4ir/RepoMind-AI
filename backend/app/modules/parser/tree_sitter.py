"""Tree-sitter grammar loading and parsing isolated from parser orchestration."""

from pathlib import Path
from typing import Any

from app.modules.parser.exceptions import TreeSitterUnavailableError
from app.modules.parser.language import SupportedLanguage


class TreeSitterParser:
    """Cache configured Tree-sitter parsers for supported source languages."""

    def __init__(self) -> None:
        self._parsers: dict[tuple[SupportedLanguage, bool], Any] = {}

    def parse(self, source: bytes, language: SupportedLanguage, path: str | Path) -> Any:
        """Return a Tree-sitter tree for a supported source file."""
        is_tsx = Path(path).suffix.lower() == ".tsx"
        key = (language, is_tsx)
        parser = self._parsers.get(key)
        if parser is None:
            parser = self._build_parser(language, is_tsx)
            self._parsers[key] = parser
        return parser.parse(source)

    @staticmethod
    def _build_parser(language: SupportedLanguage, is_tsx: bool) -> Any:
        try:
            from tree_sitter import Language, Parser

            capsule = TreeSitterParser._grammar_capsule(language, is_tsx)
            grammar = capsule if isinstance(capsule, Language) else Language(capsule)
            try:
                return Parser(grammar)
            except TypeError:
                parser = Parser()
                parser.language = grammar
                return parser
        except (ImportError, TypeError, ValueError) as exc:
            raise TreeSitterUnavailableError(
                f"Tree-sitter grammar initialization failed for {language.value}."
            ) from exc

    @staticmethod
    def _grammar_capsule(language: SupportedLanguage, is_tsx: bool) -> Any:
        if language is SupportedLanguage.PYTHON:
            import tree_sitter_python

            return tree_sitter_python.language()
        if language is SupportedLanguage.JAVASCRIPT:
            import tree_sitter_javascript

            return tree_sitter_javascript.language()
        if language is SupportedLanguage.TYPESCRIPT:
            import tree_sitter_typescript

            return (
                tree_sitter_typescript.language_tsx()
                if is_tsx
                else tree_sitter_typescript.language_typescript()
            )
        raise TreeSitterUnavailableError(
            f"No Tree-sitter grammar is configured for {language.value}."
        )
