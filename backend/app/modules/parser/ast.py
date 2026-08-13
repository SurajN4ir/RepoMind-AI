"""Small Tree-sitter AST helpers isolated from language-specific visitors."""

from collections.abc import Iterator
from typing import Any


def node_text(node: Any, source: bytes) -> str:
    """Decode the source segment spanned by a Tree-sitter node."""
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def node_name(node: Any, source: bytes) -> str | None:
    """Return the name field of a declaration node when its grammar provides one."""
    name_node = node.child_by_field_name("name")
    return node_text(name_node, source) if name_node is not None else None


def walk_nodes(node: Any) -> Iterator[Any]:
    """Yield a node and all descendants in source order."""
    yield node
    for child in node.children:
        yield from walk_nodes(child)


def first_docstring(body_node: Any | None, source: bytes) -> str | None:
    """Return a Python-style leading string expression from a declaration body."""
    if body_node is None:
        return None
    named_children = [child for child in body_node.children if child.is_named]
    if not named_children or named_children[0].type != "expression_statement":
        return None
    statement = named_children[0]
    if not statement.children or statement.children[0].type not in {
        "string",
        "concatenated_string",
    }:
        return None
    return node_text(statement, source)
