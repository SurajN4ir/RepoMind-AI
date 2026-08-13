"""Unit tests for semantic chunking without filesystem or persistence dependencies."""

from app.modules.chunker.models import ChunkType
from app.modules.chunker.service import SemanticChunkerService
from app.modules.parser.language import SupportedLanguage
from app.modules.parser.models import (
    ImportReference,
    ParsedFile,
    ParsedRepository,
    ParsedSymbol,
    SymbolKind,
)
from app.shared.identifiers.uuid import new_uuid


def _parsed_file(
    path: str,
    source: str,
    *,
    language: SupportedLanguage | None = None,
    symbols: tuple[ParsedSymbol, ...] = (),
    imports: tuple[ImportReference, ...] = (),
) -> ParsedFile:
    return ParsedFile(
        path=path,
        language=language,
        symbols=symbols,
        imports=imports,
        exports=(),
        docstrings=(),
        comments=(),
        parse_error=None,
        source=source,
    )


def _repository(*files: ParsedFile) -> ParsedRepository:
    return ParsedRepository.create(new_uuid(), files)


def test_chunker_creates_class_function_and_method_chunks() -> None:
    source = """class AuthService:
    def login(self, user):
        return user

    def logout(self):
        return None

def helper():
    return True
"""
    parsed = _repository(
        _parsed_file(
            "auth.py",
            source,
            language=SupportedLanguage.PYTHON,
            symbols=(
                ParsedSymbol("AuthService", SymbolKind.CLASS, 1, 6, None),
                ParsedSymbol("login", SymbolKind.METHOD, 2, 3, "(self, user)", "AuthService"),
                ParsedSymbol("logout", SymbolKind.METHOD, 5, 6, "(self)", "AuthService"),
                ParsedSymbol("helper", SymbolKind.FUNCTION, 8, 9, "()"),
            ),
        )
    )

    collection = SemanticChunkerService().chunk(parsed)

    assert [chunk.chunk_type for chunk in collection.chunks] == [
        ChunkType.CLASS,
        ChunkType.METHOD,
        ChunkType.METHOD,
        ChunkType.FUNCTION,
    ]
    assert [chunk.qualified_symbol_name for chunk in collection.chunks] == [
        "AuthService",
        "AuthService.login",
        "AuthService.logout",
        "helper",
    ]
    assert collection.chunks[1].content.startswith("    def login")


def test_chunker_creates_markdown_heading_sections() -> None:
    parsed = _repository(
        _parsed_file(
            "README.md",
            "# Install\nRun setup.\n\n# Usage\nRun the service.\n",
        )
    )

    collection = SemanticChunkerService().chunk(parsed)

    assert [chunk.chunk_type for chunk in collection.chunks] == [
        ChunkType.README_SECTION,
        ChunkType.README_SECTION,
    ]
    assert collection.chunks[0].content == "# Install\nRun setup."


def test_chunker_creates_configuration_sections() -> None:
    parsed = _repository(
        _parsed_file(
            "config.yaml",
            "database:\n  host: localhost\nredis:\n  host: localhost\n",
        )
    )

    collection = SemanticChunkerService().chunk(parsed)

    assert [chunk.chunk_type for chunk in collection.chunks] == [ChunkType.CONFIG, ChunkType.CONFIG]
    assert collection.chunks[1].content.startswith("redis:")


def test_chunker_handles_empty_and_unsupported_repositories() -> None:
    empty_collection = SemanticChunkerService().chunk(_repository())
    unsupported_collection = SemanticChunkerService().chunk(
        _repository(_parsed_file("notes.txt", "Repository notes."))
    )

    assert empty_collection.statistics.total_chunks == 0
    assert empty_collection.statistics.average_tokens == 0.0
    assert unsupported_collection.chunks[0].chunk_type is ChunkType.UNKNOWN


def test_chunk_ids_ordering_and_metadata_are_deterministic() -> None:
    first_file = _parsed_file(
        "a.py",
        "import os\n\ndef run():\n    pass\n",
        language=SupportedLanguage.PYTHON,
        symbols=(ParsedSymbol("run", SymbolKind.FUNCTION, 3, 4, "()"),),
        imports=(ImportReference("import os", 1),),
    )
    second_file = _parsed_file(
        "z.py",
        "def last():\n    pass\n",
        language=SupportedLanguage.PYTHON,
        symbols=(ParsedSymbol("last", SymbolKind.FUNCTION, 1, 2, "()"),),
    )
    parsed = _repository(second_file, first_file)
    service = SemanticChunkerService()

    first = service.chunk(parsed)
    second = service.chunk(parsed)

    assert [chunk.file_path for chunk in first.chunks] == ["a.py", "a.py", "z.py"]
    assert [chunk.id for chunk in first.chunks] == [chunk.id for chunk in second.chunks]
    function_chunk = first.chunks[1]
    assert function_chunk.metadata["parent_symbol"] is None
    assert function_chunk.metadata["imports"] == ["import os"]
    assert function_chunk.metadata["line_range"] == {"start": 3, "end": 4}
    assert function_chunk.token_count > 0
