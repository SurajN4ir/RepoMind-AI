"""Tokenizer abstraction for transient semantic chunk token estimates."""

import re
from typing import Protocol


class Tokenizer(Protocol):
    """Count tokens without coupling chunking to an embedding-model tokenizer."""

    def count_tokens(self, text: str) -> int:
        """Return a token count for text."""


class EstimatingTokenizer:
    """A deterministic tokenizer estimate suitable until an embedding tokenizer is selected."""

    _TOKEN_PATTERN = re.compile(r"\w+|[^\s\w]", re.UNICODE)

    def count_tokens(self, text: str) -> int:
        """Estimate tokens by counting words and punctuation boundaries."""
        return len(self._TOKEN_PATTERN.findall(text))
