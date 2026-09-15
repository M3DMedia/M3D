"""Domain model for operational decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from m3d.domain.common.types import DecisionId, EvidenceId, InvestigationId, utc_now

DECISION_STATES = frozenset(
    {
        "proposed",
        "evaluated",
        "accepted",
        "rejected",
        "superseded",
    }
)


@dataclass(frozen=True, slots=True)
class Decision:
    """A determination of what should happen based on investigation findings."""

    id: DecisionId
    investigation_id: InvestigationId
    decision: str
    rationale: str
    evidence_ids: tuple[EvidenceId, ...] = ()
    confidence: float = 0.0
    status: str = "proposed"
    created_at: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the decision's required fields and state."""
        if not self.decision.strip():
            raise ValueError("Decision cannot be empty.")

        if not self.rationale.strip():
            raise ValueError("Decision rationale cannot be empty.")

        if self.status not in DECISION_STATES:
            raise ValueError(f"Invalid decision status: {self.status}")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Decision confidence must be between 0.0 and 1.0.")
