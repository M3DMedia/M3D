"""Tests for the manual authorization provider."""

import pytest

from m3d.adapters.authorization.manual import ManualAuthorizationProvider
from m3d.domain.action import Action
from m3d.domain.common.types import ActionId, DecisionId, EnvironmentId


def make_action(requested_by: str = "operator") -> Action:
    """Create a valid action for tests."""
    return Action(
        id=ActionId("action_test"),
        decision_id=DecisionId("dec_test"),
        environment_id=EnvironmentId("env_test"),
        action_type="restart_service",
        description="Restart the affected service.",
        requested_by=requested_by,
    )


def test_request_creates_pending_authorization() -> None:
    provider = ManualAuthorizationProvider()
    action = make_action()

    authorization = provider.request(action)

    assert authorization.action_id == action.id
    assert authorization.requested_by == action.requested_by
    assert authorization.status == "requested"
    assert authorization.metadata["authorization_method"] == "manual"


def test_request_generates_unique_authorization_ids() -> None:
    provider = ManualAuthorizationProvider()
    action = make_action()

    first = provider.request(action)
    second = provider.request(action)

    assert first.id != second.id


def test_request_rejects_empty_requester() -> None:
    provider = ManualAuthorizationProvider()
    action = make_action(" ")

    with pytest.raises(ValueError, match="Action requester cannot be empty"):
        provider.request(action)
