"""Convert semantic chunks to provider-agnostic index documents."""

from app.modules.chunker.models import Chunk
from app.modules.embedding.models import IndexDocument


class ChunkDocumentTransformer:
    """Format chunk metadata and content into stable provider-facing embedding text."""

    def transform(self, chunk: Chunk) -> IndexDocument:
        """Transform one semantic chunk without exposing the Chunk type to providers."""
        headers = [
            f"File: {chunk.file_path}",
            f"Language: {chunk.language.value if chunk.language else 'unknown'}",
            f"Type: {chunk.chunk_type.value}",
        ]
        if chunk.qualified_symbol_name:
            headers.insert(0, f"Symbol: {chunk.qualified_symbol_name}")
        metadata = {
            "repository_id": str(chunk.repository_id),
            "file_path": chunk.file_path,
            "qualified_symbol_name": chunk.qualified_symbol_name,
            "language": chunk.language.value if chunk.language else None,
            "chunk_type": chunk.chunk_type.value,
            **chunk.metadata,
        }
        return IndexDocument(
            id=chunk.id,
            text="\n".join(headers) + f"\n\n{chunk.content}",
            metadata=metadata,
        )

    def transform_collection(self, chunks: tuple[Chunk, ...]) -> tuple[IndexDocument, ...]:
        """Transform ordered chunks while preserving their collection order."""
        return tuple(self.transform(chunk) for chunk in chunks)
