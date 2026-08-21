from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Any, Protocol


@dataclass(frozen=True)
class PublicRecordQuery:
    source_id: str
    query: str
    fields: tuple[str, ...] = ()
    jurisdiction: str | None = None


@dataclass(frozen=True)
class PublicRecordResult:
    source_id: str
    record_type: str
    source_url: str
    fields: dict[str, Any]
    observed_at: str | None = None
    source_reference: str | None = None


class PublicConnector(Protocol):
    source_id: str

    def supports(self, query: PublicRecordQuery) -> bool: ...

    async def search(self, query: PublicRecordQuery) -> list[PublicRecordResult]: ...


class ConnectorRegistry:
    def __init__(self) -> None:
        self._connectors: dict[str, PublicConnector] = {}

    def register(self, connector: PublicConnector) -> None:
        if connector.source_id in self._connectors:
            raise ValueError(f"connector already registered: {connector.source_id}")
        self._connectors[connector.source_id] = connector

    def get(self, source_id: str) -> PublicConnector | None:
        return self._connectors.get(source_id)

    def all(self) -> list[PublicConnector]:
        return list(self._connectors.values())


def host_allowed(url: str, allowed_domains: list[str]) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").casefold()
    return any(host == d.casefold() or host.endswith("." + d.casefold()) for d in allowed_domains)
