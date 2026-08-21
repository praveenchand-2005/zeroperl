from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable


@dataclass(frozen=True)
class GraphEntity:
    entity_type: str
    label: str
    external_key: str


def normalize(value: str | None) -> str:
    return " ".join((value or "").casefold().split())


def entity_key(entity_type: str, label: str) -> str:
    return f"{entity_type}:{normalize(label)}"


def similarity(left: str | None, right: str | None) -> float:
    return round(SequenceMatcher(None, normalize(left), normalize(right)).ratio(), 4)


def build_candidate_edges(person: GraphEntity, candidates: Iterable[GraphEntity]) -> list[dict]:
    rows = []
    for candidate in candidates:
        score = similarity(person.label, candidate.label)
        rows.append({
            "source": person.external_key,
            "target": candidate.external_key,
            "relationship": "POSSIBLE_MATCH",
            "score": score,
        })
    return sorted(rows, key=lambda row: row["score"], reverse=True)


def evidence_value_dedup(values: Iterable[str | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = normalize(value)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result
