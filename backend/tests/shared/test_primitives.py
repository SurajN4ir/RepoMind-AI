from datetime import UTC
from uuid import UUID

from app.shared.clock.utc import utc_now
from app.shared.identifiers.uuid import new_uuid


def test_new_uuid_returns_distinct_uuid_values() -> None:
    first = new_uuid()
    second = new_uuid()

    assert isinstance(first, UUID)
    assert first != second


def test_utc_now_returns_timezone_aware_utc_time() -> None:
    value = utc_now()

    assert value.tzinfo is UTC
