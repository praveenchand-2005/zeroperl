from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
import re
from typing import Iterable


@dataclass(frozen=True)
class CandidateRecord:
    entity_type: str
    name: str | None
    address: str | None
    city: str | None
    district: str | None = None
    state: str | None = None
    source_id: str = ""
    observed_at: datetime | None = None


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip().casefold())


def similarity(left: str | None, right: str | None) -> float:
    return round(SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio(), 4)


def candidate_score(seed: CandidateRecord, record: CandidateRecord) -> float:
    weights: list[float] = []
    if seed.name and record.name:
        weights.append(similarity(seed.name, record.name) * 0.55)
    if seed.city and record.city:
        weights.append((1.0 if normalize_text(seed.city) == normalize_text(record.city) else 0.0) * 0.15)
    if seed.district and record.district:
        weights.append((1.0 if normalize_text(seed.district) == normalize_text(record.district) else 0.0) * 0.10)
    if seed.state and record.state:
        weights.append((1.0 if normalize_text(seed.state) == normalize_text(record.state) else 0.0) * 0.10)
    if seed.address and record.address:
        weights.append(similarity(seed.address, record.address) * 0.10)
    return round(min(sum(weights), 1.0), 4)


def detect_address_conflicts(records: Iterable[CandidateRecord]) -> list[dict[str, object]]:
    normalized: dict[str, list[str]] = {}
    for record in records:
        address = normalize_text(record.address)
        if address:
            normalized.setdefault(address, []).append(record.source_id)
    if len(normalized) <= 1:
        return []
    return [
        {
            "type": "ADDRESS_CONFLICT",
            "addresses": [
                {"address": address, "sources": sources} for address, sources in normalized.items()
            ],
        }
    ]


def independent_source_count(source_ids: Iterable[str]) -> int:
    return len({source_id for source_id in source_ids if source_id})


def temporal_state(observed_at: datetime | None, now: datetime | None = None) -> str:
    if observed_at is None:
        return "UNKNOWN_DATE"
    current = now or datetime.now(timezone.utc)
    age_days = max((current - observed_at).days, 0)
    if age_days <= 90:
        return "RECENT"
    if age_days <= 730:
        return "HISTORICAL"
    return "STALE"


def address_clusters(records: Iterable[CandidateRecord]) -> dict[str, list[CandidateRecord]]:
    clusters: dict[str, list[CandidateRecord]] = {}
    for record in records:
        key = normalize_text(record.address)
        if key:
            clusters.setdefault(key, []).append(record)
    return clusters
