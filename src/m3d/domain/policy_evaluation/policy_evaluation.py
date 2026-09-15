"""Domain model for policy evaluations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from m3d.domain.common.types import DecisionId, PolicyId

POLICY_EVALUATION_STATES = frozenset(
    {
        "pending",
        "evaluated",
        "allowed",
        "denied",
        "approval_required",
    }
)


@dataclass(frozen=True, slots=True)
class PolicyEvaluation:
    """The result of evaluating a policy against an operational decision."""

    id: str
    policy_id: PolicyId
    decision_id: DecisionId
    result: str
    rationale: str
    status: str = "pending"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the policy evaluation's required fields and state."""
        if not self.id.strip():
            raise ValueError("Policy evaluation ID cannot be empty.")

        if not self.result.strip():
            raise ValueError("Policy evaluation result cannot be empty.")

        if not self.rationale.strip():
            raise ValueError("Policy evaluation rationale cannot be empty.")

        if self.status not in POLICY_EVALUATION_STATES:
            raise ValueError(f"Invalid policy evaluation status: {self.status}")
