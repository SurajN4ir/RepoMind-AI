"""Replaceable token measurement and budget-allocation policies."""

import re
from typing import Protocol

from app.modules.context_builder.exceptions import InvalidContextBudgetError
from app.modules.context_builder.models import EvidenceChunk


class TokenCounter(Protocol):
    """Estimate token usage without depending on a model vendor tokenizer."""

    def count(self, text: str) -> int:
        """Return a deterministic token estimate for text."""


class WhitespaceTokenCounter:
    """Conservative, model-neutral token estimate for early context construction."""

    def count(self, text: str) -> int:
        """Count lexical units; swap this policy for model-specific tokenizers later."""
        return len(re.findall(r"\S+", text))


class BudgetAllocator:
    """Retain ordered evidence until a configured cumulative token budget is exhausted."""

    def __init__(self, token_budget: int = 4_000) -> None:
        if token_budget < 1:
            raise InvalidContextBudgetError("Token budget must be positive.")
        self._token_budget = token_budget

    @property
    def token_budget(self) -> int:
        """Return the fixed budget used for this allocator."""
        return self._token_budget

    def allocate(self, chunks: tuple[EvidenceChunk, ...]) -> tuple[EvidenceChunk, ...]:
        """Choose the highest ordered chunks that fit wholly inside the budget."""
        retained: list[EvidenceChunk] = []
        consumed = 0
        for chunk in chunks:
            if chunk.token_count + consumed > self._token_budget:
                continue
            retained.append(chunk)
            consumed += chunk.token_count
        return tuple(retained)
