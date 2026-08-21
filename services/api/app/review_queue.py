from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ReviewReason(StrEnum):
    AMBIGUOUS_IDENTITY = "AMBIGUOUS_IDENTITY"
    ADDRESS_CONFLICT = "ADDRESS_CONFLICT"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"


@dataclass(frozen=True)
class ReviewTask:
    case_id: str
    investigation_id: str
    reason: ReviewReason
    summary: str
    priority: str = "NORMAL"


def needs_review(confidence: float, has_conflict: bool) -> bool:
    return has_conflict or confidence < 0.75
