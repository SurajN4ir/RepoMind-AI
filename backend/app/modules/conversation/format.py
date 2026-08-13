"""Conversation history formatting for LLM context.

Kept as a standalone function — no service class, no protocol.
Reuses the existing WhitespaceTokenCounter for token estimation.
"""

from collections.abc import Sequence
from datetime import datetime

from app.modules.conversation.models import MessageRecord


def format_conversation_history(
    messages: Sequence[MessageRecord],
    token_budget: int = 2000,
) -> str:
    """Format recent conversation messages for inclusion in an LLM prompt.

    Returns messages in chronological order.  If the combined token
    count exceeds *token_budget*, oldest messages are dropped and a
    single-line note is prepended.
    """
    if not messages:
        return ""

    sections: list[str] = []
    estimated_tokens = 0
    dropped = 0

    for msg in messages:
        formatted = _format_message(msg)
        tokens = len(formatted.split())
        if estimated_tokens + tokens > token_budget:
            dropped += 1
            continue
        sections.append(formatted)
        estimated_tokens += tokens

    result = "\n".join(sections)

    if dropped > 0:
        prefix = (
            f"[Earlier conversation omitted — {dropped} message(s) dropped to fit token budget]\n"
        )
        result = prefix + result

    return result


def _format_message(msg: MessageRecord) -> str:
    label = "User" if msg.role == "user" else "Assistant"
    timestamp = ""
    if msg.created_at is not None and isinstance(msg.created_at, datetime):
        timestamp = f" ({msg.created_at.strftime('%H:%M')})"
    return f"{label}{timestamp}: {msg.content}"
