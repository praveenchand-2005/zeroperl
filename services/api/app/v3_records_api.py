from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_current_user
from .db import get_db
from .models import AuditLog, Case, Evidence, User
from .v3_intelligence import CandidateRecord, candidate_score, detect_address_conflicts, independent_source_count

router = APIRouter(prefix="/api/v3/records", tags=["V3 intelligence"])


class RecordCandidate(BaseModel):
    entity_type: str = "PERSON"
    name: str | None = None
    address: str | None = None
    city: str | None = None
    source_id: str = Field(min_length=2)
    observed_at: str | None = None


class MatchRequest(BaseModel):
    seed_name: str | None = None
    seed_city: str | None = None
    candidates: list[RecordCandidate] = Field(default_factory=list)


@router.post("/match")
async def match_records(
    case_id: UUID,
    payload: MatchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    case = await db.scalar(select(Case).where(Case.id == case_id, Case.organization_id == user.organization_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    candidates = [CandidateRecord(**candidate.model_dump()) for candidate in payload.candidates]
    ranked = []
    for candidate in candidates:
        ranked.append({
            **candidate.__dict__,
            "score": candidate_score(payload.seed_name, payload.seed_city, candidate),
        })

    ranked.sort(key=lambda row: row["score"], reverse=True)
    conflicts = detect_address_conflicts(candidates)
    sources = independent_source_count(candidate.source_id for candidate in candidates)

    db.add(AuditLog(
        organization_id=user.organization_id,
        user_id=user.id,
        case_id=case.id,
        action="V3_RECORD_MATCH",
        details=f"candidates={len(candidates)};independent_sources={sources};conflicts={len(conflicts)}",
    ))
    await db.commit()

    return {
        "case_id": str(case.id),
        "ranked_candidates": ranked,
        "independent_source_count": sources,
        "conflicts": conflicts,
    }


@router.get("/{case_id}/evidence")
async def evidence_for_case(
    case_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    case = await db.scalar(select(Case).where(Case.id == case_id, Case.organization_id == user.organization_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    rows = await db.scalars(
        select(Evidence)
        .where(Evidence.organization_id == user.organization_id, Evidence.case_id == case.id)
        .order_by(Evidence.retrieved_at.desc())
    )
    return [
        {
            "id": str(item.id),
            "source_name": item.source_name,
            "source_type": item.source_type,
            "source_url": item.source_url,
            "field_name": item.field_name,
            "value": item.normalized_value or item.raw_value,
            "confidence": item.confidence,
            "verification_status": item.verification_status,
            "retrieved_at": item.retrieved_at.isoformat(),
        }
        for item in rows.all()
    ]
