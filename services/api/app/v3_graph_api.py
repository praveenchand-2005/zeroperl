from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_current_user
from .db import get_db
from .models import Case, EvidenceEdge, EvidenceNode, User
from .v3_graph import GraphEntity, build_candidate_edges

router = APIRouter(prefix="/api/v3/graph", tags=["v3-graph"])


class GraphRequest(BaseModel):
    person_label: str = Field(min_length=1, max_length=300)
    candidates: list[dict[str, str]] = Field(default_factory=list)


@router.post("/{case_id}/preview")
async def graph_preview(
    case_id: UUID,
    payload: GraphRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    case = await db.scalar(select(Case).where(Case.id == case_id, Case.organization_id == user.organization_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    person = GraphEntity("PERSON", payload.person_label, f"PERSON:{payload.person_label}")
    candidates = [GraphEntity(item.get("entity_type", "UNKNOWN"), item.get("label", ""), item.get("external_key", "")) for item in payload.candidates]
    return {"case_id": str(case.id), "edges": build_candidate_edges(person, candidates)}


@router.get("/{case_id}")
async def case_graph(
    case_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    case = await db.scalar(select(Case).where(Case.id == case_id, Case.organization_id == user.organization_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    nodes = await db.scalars(select(EvidenceNode).where(EvidenceNode.organization_id == user.organization_id, EvidenceNode.case_id == case.id))
    edges = await db.scalars(select(EvidenceEdge).where(EvidenceEdge.organization_id == user.organization_id, EvidenceEdge.case_id == case.id))
    return {
        "case_id": str(case.id),
        "nodes": [{"id": str(n.id), "type": n.node_type, "label": n.label, "external_key": n.external_key} for n in nodes.all()],
        "edges": [{"id": str(e.id), "source": str(e.source_node_id), "target": str(e.target_node_id), "relationship": e.relationship, "confidence": e.confidence, "verification_status": e.verification_status} for e in edges.all()],
    }
