from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EvidenceNode:
    node_id: str
    node_type: str
    label: str


@dataclass(frozen=True)
class EvidenceEdge:
    edge_id: str
    source_node: str
    target_node: str
    relationship: str
    evidence_id: str
    confidence: float | None = None
    observed_at: datetime | None = None


@dataclass(frozen=True)
class GraphSnapshot:
    nodes: tuple[EvidenceNode, ...]
    edges: tuple[EvidenceEdge, ...]


def build_snapshot(rows: list[dict[str, object]]) -> GraphSnapshot:
    nodes: dict[str, EvidenceNode] = {}
    edges: list[EvidenceEdge] = []
    for row in rows:
        source_id = str(row["source_node"])
        target_id = str(row["target_node"])
        nodes.setdefault(source_id, EvidenceNode(source_id, str(row.get("source_type", "ENTITY")), str(row.get("source_label", source_id))))
        nodes.setdefault(target_id, EvidenceNode(target_id, str(row.get("target_type", "ENTITY")), str(row.get("target_label", target_id))))
        edges.append(
            EvidenceEdge(
                edge_id=str(row["edge_id"]),
                source_node=source_id,
                target_node=target_id,
                relationship=str(row["relationship"]),
                evidence_id=str(row["evidence_id"]),
                confidence=float(row["confidence"]) if row.get("confidence") is not None else None,
                observed_at=row.get("observed_at") if isinstance(row.get("observed_at"), datetime) else None,
            )
        )
    return GraphSnapshot(tuple(nodes.values()), tuple(edges))
