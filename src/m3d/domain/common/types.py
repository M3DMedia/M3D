"""Common domain types shared across the M3D runtime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType
from uuid import uuid4

EnvironmentId = NewType("EnvironmentId", str)
EntityId = NewType("EntityId", str)
EventId = NewType("EventId", str)
InvestigationId = NewType("InvestigationId", str)
EvidenceId = NewType("EvidenceId", str)
HypothesisId = NewType("HypothesisId", str)
DecisionId = NewType("DecisionId", str)
RiskId = NewType("RiskId", str)
PolicyId = NewType("PolicyId", str)
AuthorizationId = NewType("AuthorizationId", str)
ActionId = NewType("ActionId", str)
VerificationId = NewType("VerificationId", str)
AuditRecordId = NewType("AuditRecordId", str)


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    """Generate a stable, human-readable identifier with a namespace prefix."""
    return f"{prefix}_{uuid4().hex}"


@dataclass(frozen=True, slots=True)
class Provenance:
    """Records where and how a domain observation originated."""

    source: str
    actor: str
    method: str
    timestamp: datetime
    correlation_id: str
