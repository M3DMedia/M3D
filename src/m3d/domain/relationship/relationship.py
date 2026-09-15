"""Domain model for relationships between operational entities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from m3d.domain.common.types import EntityId, utc_now


@dataclass(frozen=True, slots=True)
class Relationship:
    """A typed relationship between two operational entities."""

    id: str
    source_entity_id: EntityId
    target_entity_id: EntityId
    type: str
    attributes: Mapping[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        """Validate the relationship's identity and topology."""
        if not self.id.strip():
            raise ValueError("Relationship ID cannot be empty.")

        if not self.type.strip():
            raise ValueError("Relationship type cannot be empty.")

        if self.source_entity_id == self.target_entity_id:
            raise ValueError("A relationship cannot connect an entity to itself.")
