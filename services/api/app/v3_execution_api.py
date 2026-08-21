from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_current_user
from .db import get_db
from .models import Case, ScraperJob, SourceRegistry, User
from .source_execution import build_connector_plan

router = APIRouter(prefix="/api/v3/execution", tags=["v3-execution"])


class ExecutionRequest(BaseModel):
    case_id: UUID
    source_id: str = Field(min_length=2)
    urls: list[str] = Field(default_factory=list)
    fields: list[str] = Field(default_factory=list)


@router.post("/plan")
async def plan_execution(
    payload: ExecutionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    case = await db.scalar(select(Case).where(Case.id == payload.case_id, Case.organization_id == user.organization_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    source = await db.scalar(
        select(SourceRegistry).where(
            SourceRegistry.source_id == payload.source_id,
            SourceRegistry.enabled.is_(True),
            (SourceRegistry.organization_id == user.organization_id) | (SourceRegistry.organization_id.is_(None)),
        )
    )
    if not source:
        raise HTTPException(status_code=404, detail="Approved source not found")

    fields = [field for field in payload.fields if not source.allowed_fields or field in source.allowed_fields]
    plans = build_connector_plan(
        seed_name=case.borrower_name,
        seed_city=None,
        urls=payload.urls,
        allowed_domains=source.allowed_domains,
        allowed_fields=fields,
        source_id=source.source_id,
        source_type=source.source_type,
    )

    jobs = []
    for plan in plans:
        job = ScraperJob(
            organization_id=user.organization_id,
            investigation_id=UUID("00000000-0000-0000-0000-000000000001"),
            source_registry_id=source.id,
            job_type="PUBLIC_FETCH",
            status="QUEUED",
            requested_url=plan.url,
            requested_fields=list(plan.fields),
        )
        jobs.append({"url": plan.url, "fields": list(plan.fields), "source_id": plan.source_id})

    return {"source_id": source.source_id, "job_count": len(jobs), "jobs": jobs}
