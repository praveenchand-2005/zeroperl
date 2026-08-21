from __future__ import annotations

from datetime import datetime, timezone


def temporal_state(observed_at: datetime | None, now: datetime | None = None) -> str:
    if observed_at is None:
        return "UNKNOWN_DATE"
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    timestamp = observed_at if observed_at.tzinfo else observed_at.replace(tzinfo=timezone.utc)
    age_days = max((current - timestamp).days, 0)
    if age_days <= 90:
        return "RECENT"
    if age_days <= 730:
        return "HISTORICAL"
    return "STALE"


def recency_weight(observed_at: datetime | None, now: datetime | None = None) -> float:
    state = temporal_state(observed_at, now)
    return {"RECENT": 1.0, "HISTORICAL": 0.6, "STALE": 0.3, "UNKNOWN_DATE": 0.2}[state]
