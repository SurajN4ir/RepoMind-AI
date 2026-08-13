"""Order-preserving index document batching with a configurable token budget."""

from dataclasses import dataclass

from app.modules.chunker.tokenizer import EstimatingTokenizer, Tokenizer
from app.modules.embedding.models import IndexDocument


@dataclass(frozen=True, slots=True)
class DocumentBatch:
    """One ordered request group and its estimated token count."""

    documents: tuple[IndexDocument, ...]
    token_count: int


class DocumentBatcher:
    """Batch documents without splitting a semantic chunk across requests."""

    def __init__(
        self,
        *,
        max_batch_size: int = 32,
        max_token_budget: int = 8_000,
        tokenizer: Tokenizer | None = None,
    ) -> None:
        if max_batch_size < 1 or max_token_budget < 1:
            raise ValueError("Batch size and token budget must be positive.")
        self._max_batch_size = max_batch_size
        self._max_token_budget = max_token_budget
        self._tokenizer = tokenizer or EstimatingTokenizer()

    def batch(self, documents: tuple[IndexDocument, ...]) -> tuple[DocumentBatch, ...]:
        """Create stable, order-preserving batches within size and token constraints."""
        batches: list[DocumentBatch] = []
        pending: list[IndexDocument] = []
        pending_tokens = 0
        for document in documents:
            token_count = self._tokenizer.count_tokens(document.text)
            exceeds_budget = pending and pending_tokens + token_count > self._max_token_budget
            exceeds_size = len(pending) >= self._max_batch_size
            if exceeds_budget or exceeds_size:
                batches.append(DocumentBatch(tuple(pending), pending_tokens))
                pending, pending_tokens = [], 0
            pending.append(document)
            pending_tokens += token_count
        if pending:
            batches.append(DocumentBatch(tuple(pending), pending_tokens))
        return tuple(batches)
