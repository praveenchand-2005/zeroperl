from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from selectolax.parser import HTMLParser

app = FastAPI(title="Recovery Intelligence Scraper", version="0.1.0")


class SourcePolicy(BaseModel):
    source_id: str
    allowed_domains: list[str] = Field(default_factory=list)
    max_requests_per_minute: int = 30
    allow_public_web: bool = True


class FetchRequest(BaseModel):
    case_id: str
    source: SourcePolicy
    url: str
    fields: list[str] = Field(default_factory=list)


class Evidence(BaseModel):
    evidence_id: str
    case_id: str
    source_id: str
    source_url: str
    retrieved_at: datetime
    content_hash: str
    title: str | None = None
    text: str
    extracted_fields: dict[str, str | None] = Field(default_factory=dict)
    verification_status: str = "UNVERIFIED"


def allowed_url(url: str, policy: SourcePolicy) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    hostname = (parsed.hostname or "").lower()
    if not policy.allow_public_web or not policy.allowed_domains:
        return False
    return any(hostname == domain.lower() or hostname.endswith("." + domain.lower()) for domain in policy.allowed_domains)


def extract_text(html: str) -> tuple[str | None, str]:
    tree = HTMLParser(html)
    title_node = tree.css_first("title")
    title = title_node.text(strip=True) if title_node else None
    for node in tree.css("script, style, noscript"):
        node.decompose()
    text = tree.body.text(separator=" ", strip=True) if tree.body else tree.text(separator=" ", strip=True)
    return title, text


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}


@app.post("/v2/fetch", response_model=Evidence)
async def fetch_public_page(request: FetchRequest) -> Evidence:
    if not allowed_url(request.url, request.source):
        raise HTTPException(status_code=403, detail="Source/domain is not permitted by policy")

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=httpx.Timeout(20.0),
        headers={"User-Agent": "RecoveryIntelligence/0.1 (+authorized-case-investigation)"},
    ) as client:
        response = await client.get(request.url)
        if response.status_code == 429:
            raise HTTPException(status_code=429, detail="Source rate limit reached")
        response.raise_for_status()

    if "text/html" not in response.headers.get("content-type", ""):
        raise HTTPException(status_code=415, detail="Only HTML is supported by this fetcher")

    title, text = extract_text(response.text)
    evidence_id = hashlib.sha256(
        f"{request.case_id}|{request.source.source_id}|{request.url}|{response.text}".encode("utf-8")
    ).hexdigest()
    content_hash = hashlib.sha256(response.text.encode("utf-8")).hexdigest()

    return Evidence(
        evidence_id=evidence_id,
        case_id=request.case_id,
        source_id=request.source.source_id,
        source_url=str(response.url),
        retrieved_at=datetime.now(timezone.utc),
        content_hash=content_hash,
        title=title,
        text=text[:200_000],
    )
