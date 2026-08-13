"""Evidence pruning policies kept separate from ordering and budgets."""

from app.modules.context_builder.models import EvidenceChunk


class EvidencePruner:
    """Remove duplicate, nested, and trivial snippets before budgeting."""

    def __init__(self, *, minimum_characters: int = 20) -> None:
        self._minimum_characters = minimum_characters

    def prune(self, chunks: tuple[EvidenceChunk, ...]) -> tuple[EvidenceChunk, ...]:
        """Preserve the first highest-priority occurrence of meaningful evidence."""
        retained: list[EvidenceChunk] = []
        seen_ids: set[str] = set()
        seen_text: set[str] = set()
        for chunk in chunks:
            normalized = " ".join(chunk.text.split())
            if len(normalized) < self._minimum_characters or chunk.chunk_id in seen_ids:
                continue
            if normalized in seen_text or self._is_nested(chunk, normalized, retained):
                continue
            seen_ids.add(chunk.chunk_id)
            seen_text.add(normalized)
            retained.append(chunk)
        return tuple(retained)

    @staticmethod
    def _is_nested(candidate: EvidenceChunk, text: str, retained: list[EvidenceChunk]) -> bool:
        """Avoid a lower-priority snippet contained by kept evidence from the same file."""
        for retained_chunk in retained:
            same_file = candidate.citation.file_path == retained_chunk.citation.file_path
            if same_file and text in " ".join(retained_chunk.text.split()):
                return True
        return False
