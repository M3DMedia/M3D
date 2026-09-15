"""Domain model for operational investigations."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any

from m3d.domain.common.types import EnvironmentId, InvestigationId

INVESTIGATION_STATES = frozenset(
    {
        "created",
        "scoping",
        "collecting",
        "analyzing",
        "hypothesis",
        "testing",
        "conclusion",
        "completed",
        "failed",
        "cancelled",
    }
)


@dataclass(frozen=True, slots=True)
class Investigation:
    """An investigation into an operational event or condition."""

    id: InvestigationId
    environment_id: EnvironmentId
    trigger: str
    objective: str
    status: str = "created"
    scope: tuple[str, ...] = ()
    started_at: datetime | None = None
    completed_at: datetime | None = None
    conclusion: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the investigation's required fields and state."""
        if not self.trigger.strip():
            raise ValueError("Investigation trigger cannot be empty.")

        if not self.objective.strip():
            raise ValueError("Investigation objective cannot be empty.")

        if self.status not in INVESTIGATION_STATES:
            raise ValueError(f"Invalid investigation status: {self.status}")

    def transition_to(self, target: str) -> Investigation:
        """Return a new investigation with a validated target state."""
        from m3d.domain.investigation.transitions import transition

        new_status = transition(self.status, target)
        return replace(self, status=new_status)
