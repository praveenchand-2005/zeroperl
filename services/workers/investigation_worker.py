from __future__ import annotations

import os
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from services.api.app.models import Case, Evidence, Investigation, ScraperJob, SourceRegistry

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://recovery:recovery@localhost:5432/recovery_intelligence",
)
SCRAPER_URL = os.getenv("SCRAPER_URL", "http://localhost:8001")
engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def persist_evidence(session: AsyncSession, job: ScraperJob, case: Case, result: dict) -> int:
    content_hash = result.get("content_hash")
    if not content_hash:
        return 0

    existing = await session.scalar(
        select(Evidence).where(
            Evidence.organization_id == job.organization_id,
            Evidence.investigation_id == job.investigation_id,
            Evidence.content_hash == content_hash,
        )
    )
    if existing:
        return 0

    extracted = result.get("extracted_fields") or {}
    metadata = {
        "evidence_id": result.get("evidence_id"),
        "provenance": result.get("provenance") or {},
        "title": result.get("title"),
    }

    created = 0
    for field_name, value in extracted.items():
        if value is None:
            continue
        session.add(
            Evidence(
                organization_id=job.organization_id,
                case_id=case.id,
                investigation_id=job.investigation_id,
                scraper_job_id=job.id,
                source_name=job.source_registry_id and str(job.source_registry_id) or "unknown",
                source_type="PUBLIC_WEB",
                source_reference=result.get("evidence_id"),
                source_url=result.get("source_url"),
                entity_type="UNKNOWN",
                field_name=field_name,
                raw_value=str(value),
                normalized_value=str(value),
                observed_at=result.get("retrieved_at"),
                verification_status=result.get("verification_status", "UNVERIFIED"),
                confidence=None,
                content_hash=content_hash,
                extraction_method=result.get("extraction_method"),
                metadata=metadata,
            )
        )
        created += 1

    if not extracted:
        session.add(
            Evidence(
                organization_id=job.organization_id,
                case_id=case.id,
                investigation_id=job.investigation_id,
                scraper_job_id=job.id,
                source_name=str(job.source_registry_id),
                source_type="PUBLIC_WEB",
                source_reference=result.get("evidence_id"),
                source_url=result.get("source_url"),
                entity_type="DOCUMENT",
                field_name="document",
                raw_value=result.get("text", "")[:200000],
                normalized_value=None,
                verification_status=result.get("verification_status", "UNVERIFIED"),
                content_hash=content_hash,
                extraction_method=result.get("extraction_method"),
                metadata=metadata,
            )
        )
        created = 1

    return created


async def process_one(session: AsyncSession, job: ScraperJob) -> dict:
    if not job.requested_url or not job.source_registry_id:
        job.status = "FAILED"
        job.error_code = "INVALID_JOB"
        job.error_message = "Missing source registry or URL"
        return {"status": job.status, "job_id": str(job.id)}

    source = await session.scalar(select(SourceRegistry).where(SourceRegistry.id == job.source_registry_id))
    investigation = await session.scalar(select(Investigation).where(Investigation.id == job.investigation_id))
    if not source or not source.enabled:
        job.status = "FAILED"
        job.error_code = "SOURCE_DISABLED"
        job.error_message = "Source is unavailable or disabled"
        return {"status": job.status, "job_id": str(job.id)}
    if not investigation:
        job.status = "FAILED"
        job.error_code = "INVESTIGATION_NOT_FOUND"
        job.error_message = "Investigation no longer exists"
        return {"status": job.status, "job_id": str(job.id)}

    case = await session.scalar(select(Case).where(Case.id == investigation.case_id))
    if not case:
        job.status = "FAILED"
        job.error_code = "CASE_NOT_FOUND"
        job.error_message = "Case no longer exists"
        return {"status": job.status, "job_id": str(job.id)}

    job.status = "RUNNING"
    job.started_at = datetime.now(timezone.utc)
    job.attempts += 1
    await session.flush()

    payload = {
        "case_id": str(case.id),
        "investigation_id": str(job.investigation_id),
        "source": {
            "source_id": source.source_id,
            "allowed_domains": source.allowed_domains,
            "max_requests_per_minute": source.rate_limit_per_minute,
            "allow_public_web": True,
            "browser_allowed": False,
        },
        "url": job.requested_url,
        "fields": list(job.requested_fields),
        "use_browser": False,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{SCRAPER_URL}/v2/fetch", json=payload)
            response.raise_for_status()
        result = response.json()
        created = await persist_evidence(session, job, case, result)
        job.status = "COMPLETED"
        job.result_count = created
        job.completed_at = datetime.now(timezone.utc)
        return {"status": job.status, "job_id": str(job.id), "evidence_created": created}
    except Exception as exc:  # noqa: BLE001
        job.status = "FAILED"
        job.error_code = "SCRAPER_ERROR"
        job.error_message = str(exc)[:1000]
        job.completed_at = datetime.now(timezone.utc)
        return {"status": job.status, "job_id": str(job.id)}


async def run_once() -> list[dict]:
    async with SessionLocal() as session:
        jobs = list((await session.scalars(
            select(ScraperJob)
            .where(ScraperJob.status == "QUEUED")
            .order_by(ScraperJob.created_at)
            .limit(10)
        )).all())
        results = []
        for job in jobs:
            results.append(await process_one(session, job))

        investigation_ids = {job.investigation_id for job in jobs}
        for investigation_id in investigation_ids:
            remaining = list((await session.scalars(
                select(ScraperJob).where(
                    ScraperJob.investigation_id == investigation_id,
                    ScraperJob.status.in_(["QUEUED", "RUNNING"]),
                )
            )).all())
            failed = await session.scalar(
                select(ScraperJob.id).where(
                    ScraperJob.investigation_id == investigation_id,
                    ScraperJob.status == "FAILED",
                ).limit(1)
            )
            investigation = await session.scalar(select(Investigation).where(Investigation.id == investigation_id))
            if investigation and not remaining:
                investigation.status = "PARTIAL" if failed else "COMPLETED"
                investigation.completed_at = datetime.now(timezone.utc)

        await session.commit()
        return results


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(run_once()))
