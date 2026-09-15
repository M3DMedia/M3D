"""Domain model for operational entities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from m3d.domain.common.types import EntityId, EnvironmentId, utc_now


@dataclass(frozen=True, slots=True)
class Entity:
    """A resource, service, process, or other object inside an environment."""

    id: EntityId
    environment_id: EnvironmentId
    type: str
    name: str
    status: str
    attributes: Mapping[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        """Validate the entity's required identity fields."""
        if not self.type.strip():
            raise ValueError("Entity type cannot be empty.")

        if not self.name.strip():
            raise ValueError("Entity name cannot be empty.")

        if not self.status.strip():
            raise ValueError("Entity status cannot be empty.")
