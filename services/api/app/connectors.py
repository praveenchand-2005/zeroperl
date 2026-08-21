from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse


@dataclass(frozen=True)
class ConnectorContext:
    source_id: str
    source_type: str
    allowed_domains: tuple[str, ...]
    allowed_fields: tuple[str, ...]


@dataclass(frozen=True)
class ConnectorResult:
    source_id: str
    source_type: str
    source_reference: str
    title: str | None
    records: tuple[dict[str, str | None], ...]


class PublicConnector(Protocol):
    name: str
    source_type: str

    def can_handle(self, url: str, context: ConnectorContext) -> bool: ...

    async def collect(self, url: str, context: ConnectorContext) -> ConnectorResult: ...


def domain_allowed(url: str, allowed_domains: tuple[str, ...]) -> bool:
    host = (urlparse(url).hostname or "").casefold()
    return bool(host) and any(host == d.casefold() or host.endswith("." + d.casefold()) for d in allowed_domains)


class GenericPublicConnector:
    name = "generic-public"
    source_type = "PUBLIC_WEB"

    def can_handle(self, url: str, context: ConnectorContext) -> bool:
        return context.source_type == self.source_type and domain_allowed(url, context.allowed_domains)

    async def collect(self, url: str, context: ConnectorContext) -> ConnectorResult:
        # Actual acquisition is delegated to the scraper service. This adapter owns
        # source classification and the normalized result contract only.
        return ConnectorResult(
            source_id=context.source_id,
            source_type=context.source_type,
            source_reference=url,
            title=None,
            records=(),
        )


class GovernmentPublicConnector(GenericPublicConnector):
    name = "government-public"
    source_type = "GOVERNMENT_PUBLIC"


class RegulatoryPublicConnector(GenericPublicConnector):
    name = "regulatory-public"
    source_type = "REGULATORY_PUBLIC"


class CorporatePublicConnector(GenericPublicConnector):
    name = "corporate-public"
    source_type = "CORPORATE_PUBLIC"


CONNECTORS: tuple[PublicConnector, ...] = (
    GovernmentPublicConnector(),
    RegulatoryPublicConnector(),
    CorporatePublicConnector(),
    GenericPublicConnector(),
)


def select_connector(url: str, context: ConnectorContext) -> PublicConnector | None:
    for connector in CONNECTORS:
        if connector.can_handle(url, context):
            return connector
    return None
