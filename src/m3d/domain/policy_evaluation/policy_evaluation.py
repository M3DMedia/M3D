"""Domain model for policy evaluations."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any

from m3d.domain.common.types import DecisionId, PolicyId
from m3d.domain.policy_evaluation.transitions import (
    POLICY_EVALUATION_STATES,
    transition,
)


@dataclass(frozen=True, slots=True)
class PolicyEvaluation:
    """An evaluation of a decision against an operational policy."""

    id: str
    decision_id: DecisionId
    policy_id: PolicyId
    result: str | None = None
    reason: str | None = None
    status: str = "pending"
    evaluated_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the policy evaluation's required fields and state."""
        if not self.id.strip():
            raise ValueError("Policy evaluation ID cannot be empty.")

        if self.status not in POLICY_EVALUATION_STATES:
            raise ValueError(f"Invalid policy evaluation state: {self.status}")

    def transition_to(self, target: str) -> PolicyEvaluation:
        """Return a new policy evaluation with a validated target state."""
        new_status = transition(self.status, target)
        return replace(self, status=new_status)
