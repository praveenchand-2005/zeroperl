from worker import build_job, mark_complete, mark_retry, mark_running


def test_job_lifecycle():
    job = build_job(
        organization_id="org",
        case_id="case",
        investigation_id="inv",
        source_id="source",
        url="https://example.com",
    )
    assert job.status == "QUEUED"
    mark_running(job)
    assert job.status == "RUNNING"
    assert mark_retry(job, "temporary") is True
    assert job.status == "RETRY_WAIT"
    mark_running(job)
    mark_complete(job)
    assert job.status == "COMPLETED"


def test_job_fails_after_attempt_limit():
    job = build_job(
        organization_id="org",
        case_id="case",
        investigation_id="inv",
        source_id="source",
        url="https://example.com",
    )
    for _ in range(job.max_attempts - 1):
        assert mark_retry(job, "temporary") is True
    assert mark_retry(job, "final") is False
    assert job.status == "FAILED"
