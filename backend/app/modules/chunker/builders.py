"""Deterministic semantic chunk construction."""

from collections.abc import Iterable
from hashlib import sha256
from uuid import UUID

from app.modules.chunker.models import Chunk, ChunkType
from app.modules.chunker.tokenizer import Tokenizer
from app.modules.parser.language import SupportedLanguage
from app.modules.parser.models import ExportReference, ImportReference, ParsedSymbol, SymbolKind


class ChunkBuilder:
    """Build richly annotated chunks with stable content-independent identifiers."""

    def __init__(self, tokenizer: Tokenizer) -> None:
        self._tokenizer = tokenizer

    def build(
        self,
        *,
        repository_id: UUID,
        file_path: str,
        language: SupportedLanguage | None,
        content: str,
        start_line: int,
        end_line: int,
        chunk_type: ChunkType,
        symbol: ParsedSymbol | None = None,
        imports: Iterable[ImportReference] = (),
        exports: Iterable[ExportReference] = (),
    ) -> Chunk:
        """Build one chunk with stable identity and retrieval-oriented metadata."""
        symbol_name = symbol.name if symbol else None
        parent_name = symbol.parent_name if symbol else None
        qualified_name = self._qualified_name(symbol)
        stable_key = "|".join(
            (
                str(repository_id),
                file_path,
                qualified_name or "",
                str(start_line),
                str(end_line),
                chunk_type.value,
            )
        )
        metadata: dict[str, object] = {
            "repository_id": str(repository_id),
            "file_path": file_path,
            "language": language.value if language else None,
            "qualified_symbol_name": qualified_name,
            "symbol_kind": symbol.kind.value if symbol else None,
            "line_range": {"start": start_line, "end": end_line},
            "parent_symbol": parent_name,
            "imports": [reference.statement for reference in imports],
            "exports": [reference.statement for reference in exports],
        }
        return Chunk(
            id=sha256(stable_key.encode("utf-8")).hexdigest(),
            repository_id=repository_id,
            file_path=file_path,
            language=language,
            symbol_name=symbol_name,
            qualified_symbol_name=qualified_name,
            symbol_kind=symbol.kind if symbol else None,
            content=content,
            start_line=start_line,
            end_line=end_line,
            token_count=self._tokenizer.count_tokens(content),
            chunk_type=chunk_type,
            metadata=metadata,
        )

    @staticmethod
    def _qualified_name(symbol: ParsedSymbol | None) -> str | None:
        if symbol is None:
            return None
        return f"{symbol.parent_name}.{symbol.name}" if symbol.parent_name else symbol.name


def chunk_type_for_symbol(symbol_kind: SymbolKind) -> ChunkType:
    """Map parser symbol kinds to their semantic chunk type."""
    return {
        SymbolKind.CLASS: ChunkType.CLASS,
        SymbolKind.FUNCTION: ChunkType.FUNCTION,
        SymbolKind.METHOD: ChunkType.METHOD,
    }[symbol_kind]
