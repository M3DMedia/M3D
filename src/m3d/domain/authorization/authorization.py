"""Domain model for operational authorizations."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any

from m3d.domain.common.types import ActionId, AuthorizationId, utc_now

AUTHORIZATION_STATES = frozenset(
    {
        "requested",
        "granted",
        "denied",
        "expired",
    }
)


@dataclass(frozen=True, slots=True)
class Authorization:
    """An authorization governing whether an operational action may proceed."""

    id: AuthorizationId
    action_id: ActionId
    requested_by: str
    status: str = "requested"
    granted_by: str | None = None
    reason: str | None = None
    requested_at: datetime = field(default_factory=utc_now)
    resolved_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the authorization's required fields and state."""
        if not self.id.strip():
            raise ValueError("Authorization ID cannot be empty.")

        if not self.requested_by.strip():
            raise ValueError("Authorization requester cannot be empty.")

        if self.status not in AUTHORIZATION_STATES:
            raise ValueError(f"Invalid authorization state: {self.status}")

    def transition_to(self, target: str) -> Authorization:
        """Return a new authorization with a validated target state."""
        from m3d.domain.authorization.transitions import transition

        new_status = transition(self.status, target)
        return replace(self, status=new_status)
