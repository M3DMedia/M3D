"""Domain model for operational action results."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from m3d.domain.common.types import ActionId, EntityId, utc_now

ACTION_RESULT_STATUSES = frozenset(
    {
        "succeeded",
        "failed",
        "partial",
        "timed_out",
        "cancelled",
    }
)


@dataclass(frozen=True, slots=True)
class ActionResult:
    """The observed outcome of an executed operational action."""

    id: str
    action_id: ActionId
    status: str
    output: str | None = None
    error: str | None = None
    affected_entities: tuple[EntityId, ...] = ()
    started_at: datetime = field(default_factory=utc_now)
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the action result's required fields and status."""
        if not self.id.strip():
            raise ValueError("Action result ID cannot be empty.")

        if self.status not in ACTION_RESULT_STATUSES:
            raise ValueError(f"Invalid action result status: {self.status}")

        if self.status == "failed" and not self.error:
            raise ValueError("Failed action results must contain an error.")
