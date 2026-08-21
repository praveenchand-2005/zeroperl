from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from .auth import get_current_user
from .connector_registry import ConnectorRegistry, PublicRecordQuery
from .v3_search_planner import SearchSeed, build_queries

router = APIRouter(prefix="/api/v3/connectors", tags=["V3 connectors"])
registry = ConnectorRegistry()


class PlanRequest(BaseModel):
    name: str | None = None
    city: str | None = None
    district: str | None = None
    state: str | None = None
    business: str | None = None
    source_ids: list[str] = Field(default_factory=list)


@router.post("/plan")
async def plan_connector_queries(payload: PlanRequest, user=Depends(get_current_user)) -> dict:
    seed = SearchSeed(
        name=payload.name,
        city=payload.city,
        district=payload.district,
        state=payload.state,
        business=payload.business,
    )
    queries = build_queries(seed)
    source_ids = payload.source_ids or [connector.source_id for connector in registry.all()]
    plans = [
        {
            "source_id": source_id,
            "query": query,
            "allowed_fields": ["name", "address", "city", "district", "state", "business"],
        }
        for source_id in source_ids
        for query in queries
    ]
    return {
        "organization_id": str(user.organization_id),
        "query_count": len(plans),
        "plans": plans,
        "note": "Execution must still pass organization source-policy checks before a connector is invoked.",
    }


@router.get("/catalog")
async def connector_catalog(user=Depends(get_current_user)) -> dict:
    return {
        "organization_id": str(user.organization_id),
        "connectors": [
            {"source_id": connector.source_id, "status": "REGISTERED"}
            for connector in registry.all()
        ],
    }
