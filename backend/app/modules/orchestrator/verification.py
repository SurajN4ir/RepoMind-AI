"""Post-generation verification hooks independent from generation providers."""

from typing import Protocol

from app.modules.context_builder.models import LLMContext
from app.modules.orchestrator.models import GeneratedResponse


class ResponseVerifier(Protocol):
    """Validate a generated response against bounded evidence."""

    async def verify(self, response: GeneratedResponse, context: LLMContext) -> bool:
        """Return whether the response satisfies the configured verification policy."""


class CitationPreservationVerifier:
    """Ensure response citations originated in the prepared evidence context."""

    async def verify(self, response: GeneratedResponse, context: LLMContext) -> bool:
        """Validate chunk IDs only; this verifier intentionally makes no truth claims."""
        permitted = {citation.chunk_id for citation in context.citations}
        return all(citation.chunk_id in permitted for citation in response.citations)
