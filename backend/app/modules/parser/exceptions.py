"""Semantic parser bounded-context exceptions."""


class ParserError(Exception):
    """Base exception for semantic parsing failures."""


class TreeSitterUnavailableError(ParserError):
    """Raised when a required Tree-sitter grammar cannot be initialized."""


class SourceRootError(ParserError):
    """Raised when a manifest file resolves outside the supplied source root."""
