from datetime import datetime, timezone

from .address_intelligence import AddressObservation, current_candidates, history, normalize_address


def test_normalize_address() -> None:
    assert normalize_address("12/3, Main Road.") == "12/3 main road"


def test_history_orders_observations() -> None:
    first = AddressObservation("A", "s1", datetime(2024, 1, 1, tzinfo=timezone.utc))
    second = AddressObservation("B", "s2", datetime(2025, 1, 1, tzinfo=timezone.utc))
    rows = history([second, first])
    assert rows[0]["address"] == "A"
    assert rows[1]["address"] == "B"


def test_current_candidates_filters_old_observations() -> None:
    now = datetime(2026, 8, 21, tzinfo=timezone.utc)
    recent = AddressObservation("A", "s1", datetime(2026, 8, 1, tzinfo=timezone.utc))
    old = AddressObservation("B", "s2", datetime(2025, 1, 1, tzinfo=timezone.utc))
    candidates = current_candidates([old, recent], max_age_days=180)
    assert [item.raw_address for item in candidates] == ["A"]
