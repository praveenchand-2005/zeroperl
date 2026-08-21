from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from fetchers import fetch_browser, fetch_http
from parsers import build_provenance, parse_document

app = FastAPI(title="Recovery Intelligence Scraper", version="0.2.0")


class SourcePolicy(BaseModel):
    source_id: str
    allowed_domains: list[str] = Field(default_factory=list)
    max_requests_per_minute: int = 30
    allow_public_web: bool = True
    browser_allowed: bool = False


class FetchRequest(BaseModel):
    case_id: str
    investigation_id: str
    source: SourcePolicy
    url: str
    fields: list[str] = Field(default_factory=list)
    use_browser: bool = False


class Evidence(BaseModel):
    evidence_id: str
    case_id: str
    investigation_id: str
    source_id: str
    source_url: str
    retrieved_at: datetime
    content_hash: str
    title: str | None = None
    text: str
    extracted_fields: dict[str, str | None] = Field(default_factory=dict)
    verification_status: str = "UNVERIFIED"
    extraction_method: str
    provenance: dict[str, str]


def allowed_url(url: str, policy: SourcePolicy) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    hostname = (parsed.hostname or "").lower()
    if not policy.allow_public_web or not policy.allowed_domains:
        return False
    return any(hostname == domain.lower() or hostname.endswith("." + domain.lower()) for domain in policy.allowed_domains)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.2.0"}


@app.post("/v2/fetch", response_model=Evidence)
async def fetch_source(request: FetchRequest) -> Evidence:
    if not allowed_url(request.url, request.source):
        raise HTTPException(status_code=403, detail="Source/domain is not permitted by policy")
    if request.use_browser and not request.source.browser_allowed:
        raise HTTPException(status_code=403, detail="Browser access is disabled for this source policy")

    try:
        result = await (
            fetch_browser(request.url, request.source.allowed_domains)
            if request.use_browser
            else fetch_http(request.url, request.source.allowed_domains)
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Source fetch failed: {exc}") from exc

    title, text, extracted_fields, extraction_method = parse_document(result.body, result.content_type)
    content_hash = hashlib.sha256(result.body).hexdigest()
    evidence_id = hashlib.sha256(
        f"{request.case_id}|{request.investigation_id}|{request.source.source_id}|{result.final_url}|{content_hash}".encode("utf-8")
    ).hexdigest()

    return Evidence(
        evidence_id=evidence_id,
        case_id=request.case_id,
        investigation_id=request.investigation_id,
        source_id=request.source.source_id,
        source_url=result.final_url,
        retrieved_at=datetime.now(timezone.utc),
        content_hash=content_hash,
        title=title,
        text=text,
        extracted_fields=extracted_fields,
        extraction_method=extraction_method,
        provenance=build_provenance(result.final_url, content_hash, extraction_method),
    )
