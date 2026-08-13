"""Boundary validation for user input and derived query values."""

from app.modules.query_engine.exceptions import InvalidUserRequestError
from app.modules.query_engine.models import UserRequest


class UserRequestValidator:
    """Validate query-engine inputs before any repository resolution occurs."""

    def validate(self, request: UserRequest, normalized_text: str) -> None:
        """Reject invalid requests before their query plan can reach Retrieval."""
        if not isinstance(request.text, str) or not normalized_text:
            raise InvalidUserRequestError("Request text must not be blank.")
        limit = request.preferences.get("limit")
        if limit is not None and (
            not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100
        ):
            raise InvalidUserRequestError("Requested limit must be an integer between 1 and 100.")
        offset = request.preferences.get("offset")
        if offset is not None and (
            not isinstance(offset, int) or isinstance(offset, bool) or offset < 0
        ):
            raise InvalidUserRequestError("Requested offset must be a non-negative integer.")
