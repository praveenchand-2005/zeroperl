from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable


@dataclass(frozen=True)
class CandidateRecord:
    entity_type: str
    name: str | None
    address: str | None
    city: str | None
    source_id: str
    observed_at: str | None = None


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.casefold().split())


def similarity(left: str | None, right: str | None) -> float:
    return round(SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio(), 4)


def candidate_score(seed_name: str | None, seed_city: str | None, record: CandidateRecord) -> float:
    name_score = similarity(seed_name, record.name)
    city_score = similarity(seed_city, record.city)
    return round((name_score * 0.75) + (city_score * 0.25), 4)


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
    return len({source_id for source_id in source_ids})
