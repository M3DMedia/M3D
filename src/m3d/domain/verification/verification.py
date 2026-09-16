"""Domain model for operational verification."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any

from m3d.domain.common.types import ActionId, VerificationId, utc_now

VERIFICATION_STATES = frozenset(
    {
        "pending",
        "in_progress",
        "verified",
        "failed",
        "inconclusive",
    }
)


@dataclass(frozen=True, slots=True)
class Verification:
    """Verification of whether an intended operational outcome was achieved."""

    id: VerificationId
    action_id: ActionId
    expected_outcome: str
    status: str = "pending"
    observed_outcome: str | None = None
    verified_at: datetime | None = None
    reason: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the verification's required fields and state."""
        if not self.id.strip():
            raise ValueError("Verification ID cannot be empty.")

        if not self.expected_outcome.strip():
            raise ValueError("Expected verification outcome cannot be empty.")

        if self.status not in VERIFICATION_STATES:
            raise ValueError(f"Invalid verification state: {self.status}")

    def transition_to(self, target: str) -> Verification:
        """Return a new verification with a validated target state."""
        from m3d.domain.verification.transitions import transition

        new_status = transition(self.status, target)
        return replace(self, status=new_status)
