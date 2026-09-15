"""Common domain primitives."""

from m3d.domain.common.transitions import can_transition, transition
from m3d.domain.common.types import (
    ActionId,
    AuditRecordId,
    AuthorizationId,
    DecisionId,
    EntityId,
    EnvironmentId,
    EventId,
    EvidenceId,
    HypothesisId,
    InvestigationId,
    PolicyId,
    Provenance,
    RiskId,
    utc_now,
)

__all__ = [
    "ActionId",
    "AuditRecordId",
    "AuthorizationId",
    "DecisionId",
    "EntityId",
    "EnvironmentId",
    "EventId",
    "EvidenceId",
    "HypothesisId",
    "InvestigationId",
    "PolicyId",
    "Provenance",
    "RiskId",
    "can_transition",
    "transition",
    "utc_now",
]
