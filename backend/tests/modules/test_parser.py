"""Async semantic parser tests against temporary source workspaces."""

from pathlib import Path

import pytest

from app.modules.ingestion.manifest import RepositoryFile, RepositoryManifest, RepositoryStats
from app.modules.parser.language import LanguageDetector, SupportedLanguage
from app.modules.parser.models import SymbolKind
from app.modules.parser.service import SemanticParserService
from app.shared.identifiers.uuid import new_uuid


def _manifest(*paths: str) -> RepositoryManifest:
    files = tuple(
        RepositoryFile(path=path, size_bytes=0, extension=Path(path).suffix or None)
        for path in paths
    )
    return RepositoryManifest.create(
        new_uuid(),
        files,
        RepositoryStats(0, 0, 0, 0, 0),
    )


def test_language_detector_supports_expected_extensions() -> None:
    detector = LanguageDetector()

    assert detector.detect("service.py") is SupportedLanguage.PYTHON
    assert detector.detect("client.js") is SupportedLanguage.JAVASCRIPT
    assert detector.detect("component.tsx") is SupportedLanguage.TYPESCRIPT
    assert detector.detect("README.md") is None


@pytest.mark.asyncio
async def test_parser_extracts_python_semantics(tmp_path: Path) -> None:
    source = '''"""Module documentation."""
import os
from pathlib import Path
__all__ = ["Worker"]
# module comment
class Worker:
    """Worker documentation."""
    def execute(self, value: str) -> str:
        """Execute documentation."""
        return value

def run() -> None:
    pass
'''
    (tmp_path / "worker.py").write_bytes(source.encode("utf-8"))

    parsed = await SemanticParserService().parse(_manifest("worker.py"), tmp_path)
    parsed_file = parsed.files[0]

    assert parsed_file.parse_error is None
    assert {symbol.name for symbol in parsed_file.symbols} == {"Worker", "execute", "run"}
    assert {symbol.kind for symbol in parsed_file.symbols} == {
        SymbolKind.CLASS,
        SymbolKind.METHOD,
        SymbolKind.FUNCTION,
    }
    assert len(parsed_file.imports) == 2
    assert len(parsed_file.exports) == 1
    assert len(parsed_file.docstrings) == 3
    assert parsed_file.comments == ("# module comment",)
    assert parsed_file.ast is not None


@pytest.mark.asyncio
async def test_parser_extracts_javascript_and_typescript_semantics(tmp_path: Path) -> None:
    (tmp_path / "client.js").write_text(
        "import dep from 'dep'; export class Client { execute() {} } export const run = () => {};",
        encoding="utf-8",
    )
    (tmp_path / "service.ts").write_text(
        "export class Service { execute(): void {} } export function start(): void {}",
        encoding="utf-8",
    )

    parsed = await SemanticParserService().parse(_manifest("client.js", "service.ts"), tmp_path)
    javascript, typescript = parsed.files

    assert javascript.language is SupportedLanguage.JAVASCRIPT
    assert {symbol.name for symbol in javascript.symbols} == {"Client", "execute", "run"}
    assert len(javascript.imports) == 1
    assert len(javascript.exports) == 2
    assert typescript.language is SupportedLanguage.TYPESCRIPT
    assert {symbol.name for symbol in typescript.symbols} == {"Service", "execute", "start"}


@pytest.mark.asyncio
async def test_parser_continues_after_individual_file_failures(tmp_path: Path) -> None:
    (tmp_path / "valid.py").write_bytes(b"def valid() -> None:\n    pass\n")
    (tmp_path / "invalid.py").write_bytes(b"def broken(:\n")

    parsed = await SemanticParserService().parse(
        _manifest("valid.py", "invalid.py", "missing.py", "README.md"),
        tmp_path,
    )

    valid, invalid, missing, unsupported = parsed.files
    assert valid.parse_error is None
    assert invalid.parse_error == "Tree-sitter detected syntax errors."
    assert missing.parse_error is not None
    assert unsupported.language is None
    assert unsupported.parse_error is None
    assert parsed.stats.parsed_files == 1
    assert parsed.stats.failed_files == 2
