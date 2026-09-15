"""Domain model for investigation hypotheses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from m3d.domain.common.types import EvidenceId, HypothesisId, InvestigationId

HYPOTHESIS_STATES = frozenset(
    {
        "proposed",
        "testing",
        "supported",
        "weakened",
        "rejected",
        "confirmed",
    }
)


@dataclass(frozen=True, slots=True)
class Hypothesis:
    """A possible explanation being evaluated during an investigation."""

    id: HypothesisId
    investigation_id: InvestigationId
    statement: str
    status: str = "proposed"
    confidence: float = 0.0
    supporting_evidence: tuple[EvidenceId, ...] = ()
    contradicting_evidence: tuple[EvidenceId, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the hypothesis's required fields and state."""
        if not self.statement.strip():
            raise ValueError("Hypothesis statement cannot be empty.")

        if self.status not in HYPOTHESIS_STATES:
            raise ValueError(f"Invalid hypothesis status: {self.status}")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Hypothesis confidence must be between 0.0 and 1.0.")
