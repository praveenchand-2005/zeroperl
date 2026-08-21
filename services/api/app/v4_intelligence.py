from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
import re
from typing import Iterable


@dataclass(frozen=True)
class ProfileCandidate:
    platform: str
    profile_url: str
    display_name: str | None = None
    public_location: str | None = None
    public_company: str | None = None
    public_position: str | None = None
    observed_at: str | None = None


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip().casefold())


def similarity(left: str | None, right: str | None) -> float:
    return round(SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio(), 4)


def profile_match_score(seed_name: str | None, seed_location: str | None, candidate: ProfileCandidate) -> float:
    parts: list[float] = []
    if seed_name and candidate.display_name:
        parts.append(similarity(seed_name, candidate.display_name) * 0.65)
    if seed_location and candidate.public_location:
        parts.append(similarity(seed_location, candidate.public_location) * 0.20)
    if candidate.public_company:
        parts.append(0.15)
    return round(min(sum(parts), 1.0), 4)


def company_name_key(name: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", normalize_text(name))


def same_company(left: str | None, right: str | None) -> bool:
    return bool(company_name_key(left)) and company_name_key(left) == company_name_key(right)


def employment_state(end_present: bool, recently_observed: bool) -> str:
    if end_present:
        return "HISTORICAL"
    if recently_observed:
        return "CURRENT_CANDIDATE"
    return "UNKNOWN"


def relationship_requires_review(confidence: float, relationship_type: str) -> bool:
    if relationship_type == "PUBLIC_REPORTING_RELATIONSHIP":
        return confidence < 0.90
    return confidence < 0.80
