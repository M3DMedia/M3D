"""Domain model for operational authorizations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from m3d.domain.common.types import ActionId, AuthorizationId

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
    """Permission granted to execute a specific operational action."""

    id: AuthorizationId
    action_id: ActionId
    actor: str
    authority: str
    scope: str
    decision: str
    granted_at: datetime | None = None
    expires_at: datetime | None = None
    status: str = "requested"
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the authorization's required fields and state."""
        if not self.actor.strip():
            raise ValueError("Authorization actor cannot be empty.")

        if not self.authority.strip():
            raise ValueError("Authorization authority cannot be empty.")

        if not self.scope.strip():
            raise ValueError("Authorization scope cannot be empty.")

        if not self.decision.strip():
            raise ValueError("Authorization decision cannot be empty.")

        if self.status not in AUTHORIZATION_STATES:
            raise ValueError(f"Invalid authorization status: {self.status}")

        if (
            self.granted_at is not None
            and self.expires_at is not None
            and self.expires_at <= self.granted_at
        ):
            raise ValueError("Authorization expiry must be after its grant time.")
