from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from playwright.async_api import async_playwright


@dataclass(frozen=True)
class FetchResult:
    final_url: str
    content_type: str
    status_code: int
    body: bytes


def is_allowed_url(url: str, allowed_domains: list[str]) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    hostname = (parsed.hostname or "").lower().rstrip(".")
    return bool(hostname) and any(
        hostname == domain.lower().rstrip(".")
        or hostname.endswith("." + domain.lower().rstrip("."))
        for domain in allowed_domains
    )


async def fetch_http(url: str, allowed_domains: list[str]) -> FetchResult:
    if not is_allowed_url(url, allowed_domains):
        raise PermissionError("URL is outside the configured source policy")

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=httpx.Timeout(25.0),
        headers={"User-Agent": "RecoveryIntelligence/0.2 (+authorized-case-investigation)"},
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        return FetchResult(
            final_url=str(response.url),
            content_type=response.headers.get("content-type", ""),
            status_code=response.status_code,
            body=response.content,
        )


async def fetch_browser(url: str, allowed_domains: list[str]) -> FetchResult:
    if not is_allowed_url(url, allowed_domains):
        raise PermissionError("URL is outside the configured source policy")

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            body = await page.content()
            return FetchResult(
                final_url=page.url,
                content_type="text/html; charset=utf-8",
                status_code=response.status if response else 200,
                body=body.encode("utf-8"),
            )
        finally:
            await browser.close()
