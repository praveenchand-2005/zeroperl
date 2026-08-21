from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from .auth import get_current_user
from .v3_intelligence import CandidateRecord, candidate_score, detect_address_conflicts, independent_source_count
from .review_queue import needs_review

router = APIRouter(prefix="/api/v3/intelligence", tags=["v3-intelligence"])


class MatchRequest(BaseModel):
    seed_name: str | None = None
    seed_city: str | None = None
    seed_address: str | None = None
    candidates: list[CandidateRecord] = Field(default_factory=list)


@router.post("/match")
async def match_records(request: MatchRequest, user=Depends(get_current_user)) -> dict:
    seed = CandidateRecord("PERSON", request.seed_name, request.seed_address, request.seed_city, source_id="case-seed")
    ranked = sorted(
        ({"candidate": item, "score": candidate_score(seed, item)} for item in request.candidates),
        key=lambda row: row["score"],
        reverse=True,
    )
    conflicts = detect_address_conflicts(request.candidates)
    top_score = ranked[0]["score"] if ranked else 0.0
    return {
        "organization_id": str(user.organization_id),
        "ranked_candidates": ranked,
        "independent_source_count": independent_source_count(item.source_id for item in request.candidates),
        "conflicts": conflicts,
        "human_review_required": needs_review(top_score, bool(conflicts)),
    }
