"""Domain model for operational actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from m3d.domain.common.types import ActionId, DecisionId, EnvironmentId

ACTION_STATES = frozenset(
    {
        "proposed",
        "authorized",
        "executing",
        "completed",
        "failed",
        "rejected",
        "cancelled",
        "rolled_back",
    }
)


@dataclass(frozen=True, slots=True)
class Action:
    """An operational action intended to change an environment."""

    id: ActionId
    decision_id: DecisionId
    environment_id: EnvironmentId
    executor: str
    operation: str
    parameters: dict[str, Any] = field(default_factory=dict)
    status: str = "proposed"
    authorization: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate the action's required fields and state."""
        if not self.executor.strip():
            raise ValueError("Action executor cannot be empty.")

        if not self.operation.strip():
            raise ValueError("Action operation cannot be empty.")

        if self.status not in ACTION_STATES:
            raise ValueError(f"Invalid action status: {self.status}")

        if self.completed_at is not None and self.started_at is None:
            raise ValueError("Action cannot have a completion time without a start time.")

        if (
            self.started_at is not None
            and self.completed_at is not None
            and self.completed_at < self.started_at
        ):
            raise ValueError("Action completion time cannot precede its start time.")
