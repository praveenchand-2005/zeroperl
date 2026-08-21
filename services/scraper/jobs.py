from __future__ import annotations

from celery import Celery

celery_app = Celery(
    "recovery-intelligence-scraper",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def fetch_investigation_source(self, investigation_id: str, case_id: str, source_id: str, url: str, allowed_domains: list[str], use_browser: bool = False) -> dict:
    # Queue contract only. Network execution is implemented in the worker service.
    return {
        "status": "QUEUED_FOR_WORKER",
        "investigation_id": investigation_id,
        "case_id": case_id,
        "source_id": source_id,
        "url": url,
        "use_browser": use_browser,
    }
