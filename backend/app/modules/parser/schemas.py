"""Serialization contracts for semantic parser domain output."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.parser.models import ParsedRepository


class ParsedSymbolResponse(BaseModel):
    name: str
    kind: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    signature: str | None
    parent_name: str | None
    docstring: str | None


class ParsedFileResponse(BaseModel):
    path: str
    language: str | None
    symbols: list[ParsedSymbolResponse]
    imports: list[str]
    exports: list[str]
    docstrings: list[str]
    comments: list[str]
    parse_error: str | None


class ParsedRepositoryStatsResponse(BaseModel):
    total_files: int = Field(ge=0)
    supported_files: int = Field(ge=0)
    parsed_files: int = Field(ge=0)
    failed_files: int = Field(ge=0)
    total_symbols: int = Field(ge=0)


class ParsedRepositoryResponse(BaseModel):
    repository_id: UUID
    parsed_at: datetime
    files: list[ParsedFileResponse]
    stats: ParsedRepositoryStatsResponse

    @classmethod
    def from_domain(cls, parsed: ParsedRepository) -> "ParsedRepositoryResponse":
        """Map domain output without serializing Tree-sitter AST objects."""
        return cls(
            repository_id=parsed.repository_id,
            parsed_at=parsed.parsed_at,
            files=[
                ParsedFileResponse(
                    path=file.path,
                    language=file.language.value if file.language else None,
                    symbols=[
                        ParsedSymbolResponse(
                            name=symbol.name,
                            kind=symbol.kind.value,
                            start_line=symbol.start_line,
                            end_line=symbol.end_line,
                            signature=symbol.signature,
                            parent_name=symbol.parent_name,
                            docstring=symbol.docstring,
                        )
                        for symbol in file.symbols
                    ],
                    imports=[reference.statement for reference in file.imports],
                    exports=[reference.statement for reference in file.exports],
                    docstrings=list(file.docstrings),
                    comments=list(file.comments),
                    parse_error=file.parse_error,
                )
                for file in parsed.files
            ],
            stats=ParsedRepositoryStatsResponse(
                total_files=parsed.stats.total_files,
                supported_files=parsed.stats.supported_files,
                parsed_files=parsed.stats.parsed_files,
                failed_files=parsed.stats.failed_files,
                total_symbols=parsed.stats.total_symbols,
            ),
        )
