"""Domain model for immutable audit records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from m3d.domain.common.types import AuditRecordId

AUDIT_STATES = frozenset(
    {
        "created",
        "sealed",
    }
)


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """An immutable record of an operational state change or action."""

    id: AuditRecordId
    timestamp: datetime
    actor: str
    operation: str
    object_type: str
    object_id: str
    previous_state: Any = None
    new_state: Any = None
    correlation_id: str = ""
    status: str = "created"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the audit record's required fields and state."""
        if not self.actor.strip():
            raise ValueError("Audit actor cannot be empty.")

        if not self.operation.strip():
            raise ValueError("Audit operation cannot be empty.")

        if not self.object_type.strip():
            raise ValueError("Audit object type cannot be empty.")

        if not self.object_id.strip():
            raise ValueError("Audit object ID cannot be empty.")

        if self.status not in AUDIT_STATES:
            raise ValueError(f"Invalid audit status: {self.status}")

        if self.status == "sealed" and not self.correlation_id.strip():
            raise ValueError("Sealed audit records must contain a correlation ID.")
