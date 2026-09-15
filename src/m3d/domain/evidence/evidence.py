"""Domain model for investigation evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from m3d.domain.common.types import EntityId, EvidenceId, InvestigationId


@dataclass(frozen=True, slots=True)
class Evidence:
    """An observation collected during an investigation."""

    id: EvidenceId
    investigation_id: InvestigationId
    source: str
    observation: str
    collected_at: datetime
    collection_method: str
    entity_id: EntityId | None = None
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the evidence's required fields and confidence."""
        if not self.source.strip():
            raise ValueError("Evidence source cannot be empty.")

        if not self.observation.strip():
            raise ValueError("Evidence observation cannot be empty.")

        if not self.collection_method.strip():
            raise ValueError("Evidence collection method cannot be empty.")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Evidence confidence must be between 0.0 and 1.0.")
