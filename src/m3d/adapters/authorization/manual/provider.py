"""Manual authorization provider."""

from __future__ import annotations

from m3d.domain.action import Action
from m3d.domain.authorization import Authorization
from m3d.domain.common.types import AuthorizationId, new_id
from m3d.ports.authorization import AuthorizationProvider


class ManualAuthorizationProvider(AuthorizationProvider):
    """Create authorization requests that require external resolution."""

    def request(self, action: Action) -> Authorization:
        """Create a pending authorization request for an action."""
        if not action.requested_by.strip():
            raise ValueError("Action requester cannot be empty.")

        return Authorization(
            id=AuthorizationId(new_id("auth")),
            action_id=action.id,
            requested_by=action.requested_by,
            metadata={
                "authorization_method": "manual",
            },
        )
