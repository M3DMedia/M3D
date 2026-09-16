"""Domain model for immutable audit records."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any

from m3d.domain.common.types import AuditRecordId, utc_now

AUDIT_STATES = frozenset(
    {
        "created",
        "sealed",
    }
)


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """An immutable record of an operational change or decision."""

    id: AuditRecordId
    event_type: str
    actor: str
    description: str
    state: str = "created"
    correlation_id: str = ""
    timestamp: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the audit record's required fields and state."""
        if not self.id.strip():
            raise ValueError("Audit record ID cannot be empty.")

        if not self.event_type.strip():
            raise ValueError("Audit event type cannot be empty.")

        if not self.actor.strip():
            raise ValueError("Audit actor cannot be empty.")

        if not self.description.strip():
            raise ValueError("Audit description cannot be empty.")

        if self.state not in AUDIT_STATES:
            raise ValueError(f"Invalid audit state: {self.state}")

    def transition_to(self, target: str) -> AuditRecord:
        """Return a new audit record with a validated target state."""
        from m3d.domain.audit.transitions import transition

        new_state = transition(self.state, target)
        return replace(self, state=new_state)
