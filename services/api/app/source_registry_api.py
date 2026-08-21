from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_current_user, require_roles
from .db import get_db
from .models import AuditLog, SourceRegistry, User

router = APIRouter(prefix="/api/v3/sources", tags=["V3 sources"])


class SourceCreate(BaseModel):
    source_id: str = Field(min_length=2, max_length=120)
    source_name: str = Field(min_length=2, max_length=200)
    source_type: str = Field(min_length=2, max_length=60)
    base_url: str | None = None
    allowed_domains: list[str] = Field(default_factory=list)
    allowed_fields: list[str] = Field(default_factory=list)
    rate_limit_per_minute: int = Field(default=30, ge=1, le=10000)
    enabled: bool = True


@router.get("")
async def list_sources(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[SourceRegistry]:
    result = await db.scalars(
        select(SourceRegistry)
        .where(SourceRegistry.organization_id == user.organization_id)
        .order_by(SourceRegistry.source_name.asc())
    )
    return list(result.all())


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_source(
    payload: SourceCreate,
    user: User = Depends(require_roles("organization_admin")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    existing = await db.scalar(
        select(SourceRegistry).where(
            SourceRegistry.organization_id == user.organization_id,
            SourceRegistry.source_id == payload.source_id,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Source already exists")

    source = SourceRegistry(
        organization_id=user.organization_id,
        source_id=payload.source_id,
        source_name=payload.source_name,
        source_type=payload.source_type,
        base_url=payload.base_url,
        allowed_domains=payload.allowed_domains,
        allowed_fields=payload.allowed_fields,
        rate_limit_per_minute=payload.rate_limit_per_minute,
        enabled=payload.enabled,
    )
    db.add(source)
    await db.flush()
    db.add(AuditLog(
        organization_id=user.organization_id,
        user_id=user.id,
        action="SOURCE_CREATE",
        details=f"source={source.source_id}",
    ))
    await db.commit()
    return {
        "id": str(source.id),
        "source_id": source.source_id,
        "source_name": source.source_name,
        "enabled": source.enabled,
    }


@router.patch("/{source_id}")
async def set_source_enabled(
    source_id: UUID,
    enabled: bool,
    user: User = Depends(require_roles("organization_admin")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    source = await db.scalar(
        select(SourceRegistry).where(
            SourceRegistry.id == source_id,
            SourceRegistry.organization_id == user.organization_id,
        )
    )
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    source.enabled = enabled
    db.add(AuditLog(
        organization_id=user.organization_id,
        user_id=user.id,
        action="SOURCE_TOGGLE",
        details=f"source={source.source_id};enabled={enabled}",
    ))
    await db.commit()
    return {"id": str(source.id), "enabled": source.enabled}
