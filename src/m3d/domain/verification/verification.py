"""Domain model for operational verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from m3d.domain.common.types import ActionId, VerificationId

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
    """Evidence-based verification of an action's intended outcome."""

    id: VerificationId
    action_id: ActionId
    expected_outcome: str
    observations: tuple[str, ...] = ()
    status: str = "pending"
    confidence: float = 0.0
    verified_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the verification's required fields and state."""
        if not self.expected_outcome.strip():
            raise ValueError("Verification expected outcome cannot be empty.")

        if self.status not in VERIFICATION_STATES:
            raise ValueError(f"Invalid verification status: {self.status}")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Verification confidence must be between 0.0 and 1.0.")

        if self.status == "verified" and not self.observations:
            raise ValueError("Verified results must contain observations.")

        if self.status == "verified" and self.verified_at is None:
            raise ValueError("Verified results must contain a verification timestamp.")
