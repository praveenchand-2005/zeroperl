from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from io import BytesIO

from pypdf import PdfReader
from selectolax.parser import HTMLParser


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_html(data: bytes) -> tuple[str | None, str, dict[str, str | None]]:
    html = data.decode("utf-8", errors="replace")
    tree = HTMLParser(html)
    title_node = tree.css_first("title")
    title = title_node.text(strip=True) if title_node else None
    for node in tree.css("script, style, noscript"):
        node.decompose()
    text = tree.body.text(separator=" ", strip=True) if tree.body else tree.text(separator=" ", strip=True)
    fields: dict[str, str | None] = {}
    canonical = tree.css_first('link[rel="canonical"]')
    if canonical:
        fields["canonical_url"] = canonical.attributes.get("href")
    return title, text[:200_000], fields


def parse_pdf(data: bytes) -> tuple[str | None, str, dict[str, str | None]]:
    reader = PdfReader(BytesIO(data))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    return None, text[:200_000], {"page_count": str(len(reader.pages))}


def parse_document(data: bytes, content_type: str) -> tuple[str | None, str, dict[str, str | None], str]:
    normalized = content_type.lower()
    if "pdf" in normalized or data[:4] == b"%PDF":
        title, text, fields = parse_pdf(data)
        return title, text, fields, "PDF_TEXT"
    title, text, fields = parse_html(data)
    return title, text, fields, "HTML_TEXT"


def build_provenance(source_url: str, content_hash: str, extraction_method: str) -> dict[str, str]:
    return {
        "source_url": source_url,
        "content_hash": content_hash,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "extraction_method": extraction_method,
    }
