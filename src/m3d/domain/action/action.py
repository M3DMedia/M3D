"""Domain model for operational actions."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any

from m3d.domain.common.types import (
    ActionId,
    AuthorizationId,
    DecisionId,
    EnvironmentId,
    utc_now,
)

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
    """An operational action proposed or executed against an environment."""

    id: ActionId
    decision_id: DecisionId
    environment_id: EnvironmentId
    action_type: str
    description: str
    status: str = "proposed"
    authorization_id: AuthorizationId | None = None
    requested_by: str = ""
    proposed_at: datetime = field(default_factory=utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the action's required fields and state."""
        if not self.id.strip():
            raise ValueError("Action ID cannot be empty.")

        if not self.action_type.strip():
            raise ValueError("Action type cannot be empty.")

        if not self.description.strip():
            raise ValueError("Action description cannot be empty.")

        if self.status not in ACTION_STATES:
            raise ValueError(f"Invalid action state: {self.status}")

    def transition_to(self, target: str) -> Action:
        """Return a new action with a validated target state."""
        from m3d.domain.action.transitions import transition

        new_status = transition(self.status, target)
        return replace(self, status=new_status)
