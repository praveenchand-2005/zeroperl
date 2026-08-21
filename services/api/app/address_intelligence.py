from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re


@dataclass(frozen=True)
class AddressObservation:
    raw_address: str
    source_id: str
    observed_at: datetime | None = None
    verification_status: str = "UNVERIFIED"


def normalize_address(value: str) -> str:
    value = value.casefold().strip()
    value = re.sub(r"[^\w\s/-]", " ", value)
    return re.sub(r"\s+", " ", value)


def history(observations: list[AddressObservation]) -> list[dict[str, object]]:
    rows = []
    for item in sorted(observations, key=lambda x: x.observed_at or datetime.min.replace(tzinfo=timezone.utc)):
        rows.append({
            "address": item.raw_address,
            "normalized_address": normalize_address(item.raw_address),
            "source_id": item.source_id,
            "observed_at": item.observed_at.isoformat() if item.observed_at else None,
            "verification_status": item.verification_status,
        })
    return rows


def current_candidates(observations: list[AddressObservation], max_age_days: int = 180) -> list[AddressObservation]:
    now = datetime.now(timezone.utc)
    result = []
    for item in observations:
        if item.observed_at is None:
            continue
        age = (now - item.observed_at).days
        if age <= max_age_days:
            result.append(item)
    return sorted(result, key=lambda x: x.observed_at or now, reverse=True)
