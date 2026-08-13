"""Transport-neutral streaming lifecycle for completed generated responses."""

import re
from collections.abc import AsyncIterator
from typing import Protocol

from app.modules.orchestrator.models import GeneratedResponse, StreamEvent, StreamEventType


class ResponseStreamer(Protocol):
    """Stream a response as lifecycle events without requiring HTTP or SSE."""

    async def stream(self, response: GeneratedResponse) -> AsyncIterator[StreamEvent]:
        """Yield start, text, and final response events."""


class WordResponseStreamer:
    """Default deterministic stream adapter; replace with provider-native streaming later."""

    async def stream(self, response: GeneratedResponse) -> AsyncIterator[StreamEvent]:
        """Emit whitespace-preserving word chunks then the completed response."""
        yield StreamEvent(StreamEventType.START)
        for word in re.findall(r"\S+\s*", response.text):
            yield StreamEvent(StreamEventType.TEXT, text=word)
        yield StreamEvent(StreamEventType.END, response=response)
