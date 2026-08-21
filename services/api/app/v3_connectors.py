from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ConnectorRequest:
    case_id: str
    source_id: str
    seed_fields: dict[str, str]


@dataclass(frozen=True)
class PublicRecord:
    record_type: str
    source_id: str
    title: str
    reference: str | None
    fields: dict[str, str | None]
    published_at: str | None = None


class PublicRecordConnector(Protocol):
    source_type: str

    async def search(self, request: ConnectorRequest) -> list[PublicRecord]:
        ...


class ConnectorRegistry:
    def __init__(self) -> None:
        self._connectors: dict[str, PublicRecordConnector] = {}

    def register(self, connector: PublicRecordConnector) -> None:
        self._connectors[connector.source_type] = connector

    def get(self, source_type: str) -> PublicRecordConnector | None:
        return self._connectors.get(source_type)

    def source_types(self) -> list[str]:
        return sorted(self._connectors)
