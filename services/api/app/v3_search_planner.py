from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchSeed:
    name: str | None = None
    city: str | None = None
    district: str | None = None
    state: str | None = None
    business: str | None = None


def build_queries(seed: SearchSeed) -> list[str]:
    parts = [value.strip() for value in (seed.name, seed.city, seed.district, seed.state) if value and value.strip()]
    queries: list[str] = []
    if seed.name:
        queries.append(f'"{seed.name.strip()}"')
    if seed.name and seed.city:
        queries.append(f'"{seed.name.strip()}" "{seed.city.strip()}"')
    if seed.name and seed.state:
        queries.append(f'"{seed.name.strip()}" "{seed.state.strip()}"')
    if seed.name and seed.business:
        queries.append(f'"{seed.name.strip()}" "{seed.business.strip()}"')
    if not queries and parts:
        queries.append(' '.join(parts))
    return list(dict.fromkeys(queries))
