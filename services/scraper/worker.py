from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(slots=True)
class ScraperJob:
    job_id: str
    organization_id: str
    case_id: str
    investigation_id: str
    source_id: str
    url: str
    status: str = "QUEUED"
    attempts: int = 0
    max_attempts: int = 3
    error_message: str | None = None


def build_job(*, organization_id: str, case_id: str, investigation_id: str, source_id: str, url: str) -> ScraperJob:
    return ScraperJob(
        job_id=str(uuid4()),
        organization_id=organization_id,
        case_id=case_id,
        investigation_id=investigation_id,
        source_id=source_id,
        url=url,
    )


def mark_running(job: ScraperJob) -> None:
    job.status = "RUNNING"


def mark_retry(job: ScraperJob, error: str) -> bool:
    job.attempts += 1
    job.error_message = error
    if job.attempts >= job.max_attempts:
        job.status = "FAILED"
        return False
    job.status = "RETRY_WAIT"
    return True


def mark_complete(job: ScraperJob) -> None:
    job.status = "COMPLETED"
    job.error_message = None


def progress_payload(job: ScraperJob) -> dict:
    return {
        "job_id": job.job_id,
        "status": job.status,
        "attempts": job.attempts,
        "max_attempts": job.max_attempts,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
