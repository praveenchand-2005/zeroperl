from dataclasses import dataclass


@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    name: str
    domains: tuple[str, ...]
    category: str
    allowed_fields: tuple[str, ...]
    public: bool = True
    enabled: bool = True


# Production deployments should load these definitions from the organization-managed
# source registry database. Keep this bootstrap set intentionally empty.
SOURCE_REGISTRY: dict[str, SourceDefinition] = {}


def get_source(source_id: str) -> SourceDefinition:
    try:
        return SOURCE_REGISTRY[source_id]
    except KeyError as exc:
        raise KeyError(f"Unknown source: {source_id}") from exc
