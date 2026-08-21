from __future__ import annotations

import os
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from services.api.app.models import Case, Investigation, ScraperJob, SourceRegistry

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://recovery:recovery@localhost:5432/recovery_intelligence",
)
SCRAPER_URL = os.getenv("SCRAPER_URL", "http://localhost:8001")
engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


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
        job.status = "COMPLETED"
        job.result_count = 1
        job.completed_at = datetime.now(timezone.utc)
        return {"status": job.status, "job_id": str(job.id), "evidence": result}
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
        await session.commit()
        return results


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(run_once()))
