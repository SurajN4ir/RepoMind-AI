"""Language-aware AST visitors that return language-agnostic semantic objects."""

from dataclasses import dataclass
from typing import Any

from app.modules.parser.ast import first_docstring, node_name, node_text, walk_nodes
from app.modules.parser.language import SupportedLanguage
from app.modules.parser.models import ExportReference, ImportReference, ParsedSymbol, SymbolKind


@dataclass(frozen=True, slots=True)
class SemanticExtraction:
    """Semantic details extracted from one AST without exposing grammar node types."""

    symbols: tuple[ParsedSymbol, ...]
    imports: tuple[ImportReference, ...]
    exports: tuple[ExportReference, ...]
    docstrings: tuple[str, ...]
    comments: tuple[str, ...]


class SemanticVisitor:
    """Extract declarations and metadata from Python, JavaScript, and TypeScript ASTs."""

    def extract(self, tree: Any, source: bytes, language: SupportedLanguage) -> SemanticExtraction:
        """Visit a complete Tree-sitter AST and return language-agnostic semantic data."""
        root = tree.root_node
        comments = tuple(
            node_text(node, source) for node in walk_nodes(root) if node.type == "comment"
        )
        if language is SupportedLanguage.PYTHON:
            return self._extract_python(root, source, comments)
        return self._extract_javascript_family(root, source, comments)

    def _extract_python(
        self,
        root: Any,
        source: bytes,
        comments: tuple[str, ...],
    ) -> SemanticExtraction:
        symbols: list[ParsedSymbol] = []
        imports: list[ImportReference] = []
        exports: list[ExportReference] = []
        docstrings: list[str] = []

        def visit(node: Any, parent_class: str | None = None) -> None:
            if node.type in {"import_statement", "import_from_statement"}:
                imports.append(ImportReference(node_text(node, source), node.start_point.row + 1))
            if node.type == "assignment" and node_text(node, source).lstrip().startswith("__all__"):
                exports.append(ExportReference(node_text(node, source), node.start_point.row + 1))
            if node.type == "class_definition":
                name = node_name(node, source)
                body = node.child_by_field_name("body")
                docstring = first_docstring(body, source)
                if name is not None:
                    symbols.append(
                        self._symbol(node, name, SymbolKind.CLASS, None, docstring, source)
                    )
                    if docstring is not None:
                        docstrings.append(docstring)
                for child in node.children:
                    visit(child, name or parent_class)
                return
            if node.type == "function_definition":
                name = node_name(node, source)
                body = node.child_by_field_name("body")
                docstring = first_docstring(body, source)
                if name is not None:
                    kind = SymbolKind.METHOD if parent_class is not None else SymbolKind.FUNCTION
                    symbols.append(self._symbol(node, name, kind, parent_class, docstring, source))
                    if docstring is not None:
                        docstrings.append(docstring)
            for child in node.children:
                visit(child, parent_class)

        module_docstring = first_docstring(root, source)
        if module_docstring is not None:
            docstrings.append(module_docstring)
        visit(root)
        return SemanticExtraction(
            tuple(symbols),
            tuple(imports),
            tuple(exports),
            tuple(docstrings),
            comments,
        )

    def _extract_javascript_family(
        self,
        root: Any,
        source: bytes,
        comments: tuple[str, ...],
    ) -> SemanticExtraction:
        symbols: list[ParsedSymbol] = []
        imports: list[ImportReference] = []
        exports: list[ExportReference] = []

        def visit(node: Any, parent_class: str | None = None) -> None:
            if node.type == "import_statement":
                imports.append(ImportReference(node_text(node, source), node.start_point.row + 1))
            if node.type == "export_statement":
                exports.append(ExportReference(node_text(node, source), node.start_point.row + 1))
            if node.type == "class_declaration":
                name = node_name(node, source)
                if name is not None:
                    symbols.append(self._symbol(node, name, SymbolKind.CLASS, None, None, source))
                for child in node.children:
                    visit(child, name or parent_class)
                return
            if node.type in {"function_declaration", "generator_function_declaration"}:
                name = node_name(node, source)
                if name is not None:
                    kind = SymbolKind.METHOD if parent_class is not None else SymbolKind.FUNCTION
                    symbols.append(self._symbol(node, name, kind, parent_class, None, source))
            elif node.type == "method_definition":
                name = node_name(node, source)
                if name is not None:
                    symbols.append(
                        self._symbol(node, name, SymbolKind.METHOD, parent_class, None, source)
                    )
            elif node.type == "variable_declarator":
                value = node.child_by_field_name("value")
                if value is not None and value.type in {"arrow_function", "function_expression"}:
                    name = node_name(node, source)
                    if name is not None:
                        symbols.append(
                            self._symbol(
                                node,
                                name,
                                SymbolKind.FUNCTION,
                                parent_class,
                                None,
                                source,
                            )
                        )
            for child in node.children:
                visit(child, parent_class)

        visit(root)
        return SemanticExtraction(tuple(symbols), tuple(imports), tuple(exports), (), comments)

    @staticmethod
    def _symbol(
        node: Any,
        name: str,
        kind: SymbolKind,
        parent_name: str | None,
        docstring: str | None,
        source: bytes,
    ) -> ParsedSymbol:
        parameters = node.child_by_field_name("parameters")
        signature = node_text(parameters, source) if parameters is not None else None
        return ParsedSymbol(
            name=name,
            kind=kind,
            start_line=node.start_point.row + 1,
            end_line=node.end_point.row + 1,
            signature=signature,
            parent_name=parent_name,
            docstring=docstring,
        )
