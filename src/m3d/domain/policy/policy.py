"""Domain model for operational policies."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from m3d.domain.common.types import PolicyId

POLICY_STATES = frozenset(
    {
        "draft",
        "active",
        "disabled",
        "retired",
    }
)

POLICY_EFFECTS = frozenset(
    {
        "allow",
        "deny",
        "require_approval",
    }
)


@dataclass(frozen=True, slots=True)
class Policy:
    """A rule governing which operational actions are permitted."""

    id: PolicyId
    name: str
    description: str
    scope: str
    conditions: tuple[str, ...]
    effect: str
    priority: int = 0
    status: str = "draft"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the policy's required fields, state, and effect."""
        if not self.name.strip():
            raise ValueError("Policy name cannot be empty.")

        if not self.description.strip():
            raise ValueError("Policy description cannot be empty.")

        if not self.scope.strip():
            raise ValueError("Policy scope cannot be empty.")

        if not self.conditions:
            raise ValueError("Policy must contain at least one condition.")

        if any(not condition.strip() for condition in self.conditions):
            raise ValueError("Policy conditions cannot be empty.")

        if self.effect not in POLICY_EFFECTS:
            raise ValueError(f"Invalid policy effect: {self.effect}")

        if self.status not in POLICY_STATES:
            raise ValueError(f"Invalid policy status: {self.status}")

    def transition_to(self, target: str) -> Policy:
        """Return a new policy with a validated target state."""
        from m3d.domain.policy.transitions import transition

        new_status = transition(self.status, target)
        return replace(self, status=new_status)
