"""Domain model for immutable operational events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from m3d.domain.common.types import EntityId, EnvironmentId, EventId


@dataclass(frozen=True, slots=True)
class Event:
    """An immutable fact describing something that occurred."""

    id: EventId
    timestamp: datetime
    environment_id: EnvironmentId
    entity_id: EntityId | None
    type: str
    severity: str
    source: str
    previous_state: Any = None
    new_state: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""

    def __post_init__(self) -> None:
        """Validate the event's required fields."""
        if not self.type.strip():
            raise ValueError("Event type cannot be empty.")

        if not self.severity.strip():
            raise ValueError("Event severity cannot be empty.")

        if not self.source.strip():
            raise ValueError("Event source cannot be empty.")
