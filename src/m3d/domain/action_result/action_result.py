"""Domain model for operational action results."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from m3d.domain.common.types import ActionId

ACTION_RESULT_STATES = frozenset(
    {
        "succeeded",
        "failed",
        "partial",
        "cancelled",
    }
)


@dataclass(frozen=True, slots=True)
class ActionResult:
    """The actual outcome produced by executing an operational action."""

    action_id: ActionId
    status: str
    output: str | None = None
    error: str | None = None
    affected_entities: tuple[str, ...] = ()
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the action result's required fields and timestamps."""
        if self.status not in ACTION_RESULT_STATES:
            raise ValueError(f"Invalid action result status: {self.status}")

        if self.status == "failed" and not self.error:
            raise ValueError("Failed action results must contain an error.")

        if self.completed_at is not None and self.started_at is None:
            raise ValueError("Action result cannot have a completion time without a start time.")

        if (
            self.started_at is not None
            and self.completed_at is not None
            and self.completed_at < self.started_at
        ):
            raise ValueError("Action result completion time cannot precede its start time.")
