from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class ConnectorPlan:
    source_id: str
    source_type: str
    url: str
    fields: tuple[str, ...]
    reason: str


def build_connector_plan(
    *,
    seed_name: str | None,
    seed_city: str | None,
    urls: list[str],
    allowed_domains: list[str],
    allowed_fields: list[str],
    source_id: str,
    source_type: str,
) -> list[ConnectorPlan]:
    plans: list[ConnectorPlan] = []
    domains = {item.casefold().lstrip(".") for item in allowed_domains}
    fields = tuple(field for field in allowed_fields if field)
    for url in urls:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").casefold()
        permitted = any(hostname == domain or hostname.endswith("." + domain) for domain in domains)
        if not permitted or parsed.scheme not in {"http", "https"}:
            continue
        reason_parts = ["case-authorized source"]
        if seed_name:
            reason_parts.append("identity seed supplied")
        if seed_city:
            reason_parts.append("location seed supplied")
        plans.append(
            ConnectorPlan(
                source_id=source_id,
                source_type=source_type,
                url=url,
                fields=fields,
                reason="; ".join(reason_parts),
            )
        )
    return plans
