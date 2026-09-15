"""Domain model for operational risk assessments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from m3d.domain.common.types import DecisionId, RiskId

RISK_STATES = frozenset(
    {
        "assessed",
        "accepted",
        "mitigated",
        "escalated",
    }
)


@dataclass(frozen=True, slots=True)
class Risk:
    """An assessment of the potential consequences of a decision."""

    id: RiskId
    decision_id: DecisionId
    severity: str
    probability: float
    impact: str
    reversibility: str
    affected_entities: tuple[str, ...] = ()
    mitigation: str | None = None
    required_authorization: str | None = None
    status: str = "assessed"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the risk assessment's required fields and values."""
        if not self.severity.strip():
            raise ValueError("Risk severity cannot be empty.")

        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("Risk probability must be between 0.0 and 1.0.")

        if not self.impact.strip():
            raise ValueError("Risk impact cannot be empty.")

        if not self.reversibility.strip():
            raise ValueError("Risk reversibility cannot be empty.")

        if self.status not in RISK_STATES:
            raise ValueError(f"Invalid risk status: {self.status}")
