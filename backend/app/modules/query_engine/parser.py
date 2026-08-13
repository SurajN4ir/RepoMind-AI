"""Minimal request normalization kept independent from planning policy."""

import re

from app.modules.query_engine.models import UserRequest


class UserRequestParser:
    """Normalize request text without adding LLM-based query rewriting."""

    _LEADING_PHRASE = re.compile(
        r"^(?:show me|find|search for|where is|where are)\s+", re.IGNORECASE
    )

    def parse_text(self, request: UserRequest) -> str:
        """Return a normalized lexical query suitable for deterministic planning."""
        return self._LEADING_PHRASE.sub("", " ".join(request.text.split())).strip()
