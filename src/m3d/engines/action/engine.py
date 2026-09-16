"""Concrete operational action engine."""

from __future__ import annotations

from dataclasses import replace

from m3d.domain.action import Action
from m3d.domain.action_result import ActionResult
from m3d.domain.authorization import Authorization
from m3d.domain.common.types import AuthorizationId
from m3d.ports.action import ActionExecutor
from m3d.ports.authorization import AuthorizationProvider


class DefaultActionEngine:
    """Orchestrate authorization and execution of operational actions."""

    def __init__(
        self,
        authorization_provider: AuthorizationProvider,
        executor: ActionExecutor,
    ) -> None:
        self._authorization_provider = authorization_provider
        self._executor = executor

    def request_authorization(self, action: Action) -> Authorization:
        """Request authorization for a proposed action."""
        if action.status != "proposed":
            raise ValueError(f"Action must be proposed to request authorization: {action.id}")

        authorization = self._authorization_provider.request(action)

        if authorization.action_id != action.id:
            raise ValueError(f"Authorization action ID does not match action: {action.id}")

        return authorization

    def authorize(
        self,
        action: Action,
        authorization: Authorization,
    ) -> Action:
        """Attach a granted authorization and transition the action."""
        if authorization.action_id != action.id:
            raise ValueError(f"Authorization action ID does not match action: {action.id}")

        if authorization.status != "granted":
            raise ValueError(
                f"Action cannot be authorized with authorization status: {authorization.status}"
            )

        if action.status != "proposed":
            raise ValueError(f"Action must be proposed to become authorized: {action.id}")

        return replace(
            action.transition_to("authorized"),
            authorization_id=AuthorizationId(authorization.id),
        )

    def execute(self, action: Action) -> ActionResult:
        """Execute an authorized action."""
        if action.status != "authorized":
            raise ValueError(f"Action must be authorized before execution: {action.id}")

        executing = action.transition_to("executing")
        return self._executor.execute(executing)
