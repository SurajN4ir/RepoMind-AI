"""Unit and integration tests for the conversation module."""

from uuid import UUID, uuid4

from app.modules.conversation.format import format_conversation_history
from app.modules.conversation.models import ConversationRecord, MessageRecord


class TestFormatConversationHistory:
    """Tests for the standalone history formatting function."""

    def test_empty_messages_returns_empty_string(self) -> None:
        assert format_conversation_history([]) == ""

    def test_single_user_message(self) -> None:
        msg = MessageRecord(
            conversation_id=uuid4(),
            role="user",
            content="How does auth work?",
        )
        result = format_conversation_history([msg])
        assert "User: How does auth work?" in result
        assert "Assistant" not in result

    def test_user_and_assistant_messages(self) -> None:
        cid = uuid4()
        messages = [
            MessageRecord(conversation_id=cid, role="user", content="What is X?"),
            MessageRecord(conversation_id=cid, role="assistant", content="X is a function."),
        ]
        result = format_conversation_history(messages)
        assert "User: What is X?" in result
        assert "Assistant: X is a function." in result

    def test_token_budget_truncates_oldest(self) -> None:
        cid = uuid4()
        many_words = "word " * 200
        few_words = "hello world"
        messages = [
            MessageRecord(conversation_id=cid, role="user", content=many_words),
            MessageRecord(conversation_id=cid, role="assistant", content=many_words),
            MessageRecord(conversation_id=cid, role="user", content=few_words),
        ]
        result = format_conversation_history(messages, token_budget=20)
        assert "omitted" in result
        assert "hello world" in result

    def test_messages_within_budget_no_truncation(self) -> None:
        cid = uuid4()
        messages = [
            MessageRecord(conversation_id=cid, role="user", content="Hi"),
            MessageRecord(conversation_id=cid, role="assistant", content="Hello!"),
        ]
        result = format_conversation_history(messages, token_budget=100)
        assert "omitted" not in result
        assert "Hi" in result
        assert "Hello!" in result

    def test_role_labels_are_correct(self) -> None:
        cid = uuid4()
        messages = [
            MessageRecord(conversation_id=cid, role="user", content="Q"),
            MessageRecord(conversation_id=cid, role="assistant", content="A"),
        ]
        result = format_conversation_history(messages)
        lines = result.split("\n")
        assert lines[0].startswith("User")
        assert lines[1].startswith("Assistant")


class TestConversationRecord:
    """Basic domain model smoke tests."""

    def test_conversation_record_default_id(self) -> None:
        record = ConversationRecord(repository_id=uuid4())
        assert isinstance(record.id, UUID)

    def test_conversation_record_fields(self) -> None:
        repo_id = uuid4()
        conv_id = uuid4()
        record = ConversationRecord(repository_id=repo_id, id=conv_id)
        assert record.repository_id == repo_id
        assert record.id == conv_id


class TestMessageRecord:
    """Basic domain model smoke tests."""

    def test_message_record_defaults(self) -> None:
        cid = uuid4()
        msg = MessageRecord(conversation_id=cid, role="user", content="hello")
        assert isinstance(msg.id, UUID)
        assert msg.citation_json == ""

    def test_message_record_with_citations(self) -> None:
        cid = uuid4()
        msg = MessageRecord(
            conversation_id=cid,
            role="assistant",
            content="response",
            citation_json='[{"file_path": "src/main.py"}]',
        )
        assert msg.role == "assistant"
        assert '"src/main.py"' in msg.citation_json
