"""Tests for the authorization port."""

from m3d.domain.action import Action
from m3d.domain.authorization import Authorization
from m3d.domain.common.types import (
    ActionId,
    AuthorizationId,
    DecisionId,
    EnvironmentId,
)
from m3d.ports.authorization import AuthorizationProvider


class FakeAuthorizationProvider(AuthorizationProvider):
    """Minimal authorization provider for contract tests."""

    def request(self, action: Action) -> Authorization:
        return Authorization(
            id=AuthorizationId("auth_test"),
            action_id=action.id,
            requested_by=action.requested_by,
        )


def make_action() -> Action:
    """Create a valid action for contract tests."""
    return Action(
        id=ActionId("action_test"),
        decision_id=DecisionId("dec_test"),
        environment_id=EnvironmentId("env_test"),
        action_type="restart_service",
        description="Restart the affected service.",
        requested_by="operator",
    )


def test_authorization_provider_is_abstract() -> None:
    try:
        AuthorizationProvider()  # type: ignore[abstract]
    except TypeError:
        pass
    else:
        raise AssertionError("Expected TypeError")


def test_authorization_provider_returns_authorization() -> None:
    provider = FakeAuthorizationProvider()
    action = make_action()

    authorization = provider.request(action)

    assert authorization.action_id == action.id
    assert authorization.requested_by == action.requested_by
    assert authorization.status == "requested"
