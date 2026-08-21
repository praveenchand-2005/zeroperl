from datetime import timezone

from investigation_worker import parse_timestamp


def test_parse_timestamp_handles_utc_z_suffix() -> None:
    value = parse_timestamp("2026-08-21T15:00:00Z")
    assert value is not None
    assert value.tzinfo == timezone.utc


def test_parse_timestamp_rejects_invalid_value() -> None:
    assert parse_timestamp("not-a-date") is None
