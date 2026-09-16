"""Tests for the concrete action engine."""

from __future__ import annotations

from m3d.domain.action import Action
from m3d.domain.action_result import ActionResult
from m3d.domain.authorization import Authorization
from m3d.domain.common.types import (
    ActionId,
    AuthorizationId,
    DecisionId,
    EnvironmentId,
)
from m3d.engines.action import DefaultActionEngine
from m3d.ports.action import ActionExecutor
from m3d.ports.authorization import AuthorizationProvider


def make_action() -> Action:
    """Create a valid proposed action."""
    return Action(
        id=ActionId("act_test"),
        decision_id=DecisionId("dec_test"),
        environment_id=EnvironmentId("env_test"),
        action_type="restart_service",
        description="Restart the affected service.",
        requested_by="operator",
    )


class FakeAuthorizationProvider(AuthorizationProvider):
    """Authorization provider returning a configured authorization."""

    def __init__(self, authorization: Authorization) -> None:
        self.authorization = authorization

    def request(self, action: Action) -> Authorization:
        return self.authorization


class FakeActionExecutor(ActionExecutor):
    """Action executor recording execution requests."""

    def __init__(self) -> None:
        self.executed_actions: list[Action] = []

    def execute(self, action: Action) -> ActionResult:
        self.executed_actions.append(action)
        return ActionResult(
            id="result_test",
            action_id=action.id,
            status="succeeded",
        )


def make_authorization(
    action_id: ActionId,
    status: str = "requested",
) -> Authorization:
    """Create a valid authorization for an action."""
    return Authorization(
        id=AuthorizationId("auth_test"),
        action_id=action_id,
        requested_by="operator",
        status=status,
    )


def test_request_authorization_returns_provider_result() -> None:
    action = make_action()
    authorization = make_authorization(action.id)
    provider = FakeAuthorizationProvider(authorization)
    executor = FakeActionExecutor()
    engine = DefaultActionEngine(provider, executor)

    result = engine.request_authorization(action)

    assert result == authorization


def test_request_authorization_rejects_non_proposed_action() -> None:
    action = make_action().transition_to("cancelled")
    provider = FakeAuthorizationProvider(make_authorization(action.id))
    executor = FakeActionExecutor()
    engine = DefaultActionEngine(provider, executor)

    try:
        engine.request_authorization(action)
    except ValueError as exc:
        assert str(exc) == (f"Action must be proposed to request authorization: {action.id}")
    else:
        raise AssertionError("Expected ValueError")


def test_request_authorization_rejects_mismatched_authorization() -> None:
    action = make_action()
    authorization = make_authorization(ActionId("different_action"))
    provider = FakeAuthorizationProvider(authorization)
    executor = FakeActionExecutor()
    engine = DefaultActionEngine(provider, executor)

    try:
        engine.request_authorization(action)
    except ValueError as exc:
        assert str(exc) == (f"Authorization action ID does not match action: {action.id}")
    else:
        raise AssertionError("Expected ValueError")


def test_authorize_requires_granted_authorization() -> None:
    action = make_action()
    authorization = make_authorization(action.id, "requested")
    provider = FakeAuthorizationProvider(authorization)
    executor = FakeActionExecutor()
    engine = DefaultActionEngine(provider, executor)

    try:
        engine.authorize(action, authorization)
    except ValueError as exc:
        assert str(exc) == ("Action cannot be authorized with authorization status: requested")
    else:
        raise AssertionError("Expected ValueError")


def test_authorize_attaches_authorization_and_transitions_action() -> None:
    action = make_action()
    authorization = make_authorization(action.id, "granted")
    provider = FakeAuthorizationProvider(authorization)
    executor = FakeActionExecutor()
    engine = DefaultActionEngine(provider, executor)

    authorized = engine.authorize(action, authorization)

    assert authorized.status == "authorized"
    assert authorized.authorization_id == authorization.id
    assert action.status == "proposed"
    assert action.authorization_id is None


def test_authorize_rejects_mismatched_authorization() -> None:
    action = make_action()
    authorization = make_authorization(
        ActionId("different_action"),
        "granted",
    )
    provider = FakeAuthorizationProvider(authorization)
    executor = FakeActionExecutor()
    engine = DefaultActionEngine(provider, executor)

    try:
        engine.authorize(action, authorization)
    except ValueError as exc:
        assert str(exc) == (f"Authorization action ID does not match action: {action.id}")
    else:
        raise AssertionError("Expected ValueError")


def test_execute_requires_authorized_action() -> None:
    action = make_action()
    provider = FakeAuthorizationProvider(make_authorization(action.id))
    executor = FakeActionExecutor()
    engine = DefaultActionEngine(provider, executor)

    try:
        engine.execute(action)
    except ValueError as exc:
        assert str(exc) == (f"Action must be authorized before execution: {action.id}")
    else:
        raise AssertionError("Expected ValueError")

    assert executor.executed_actions == []


def test_execute_passes_executing_action_to_executor() -> None:
    action = make_action()
    authorization = make_authorization(action.id, "granted")
    provider = FakeAuthorizationProvider(authorization)
    executor = FakeActionExecutor()
    engine = DefaultActionEngine(provider, executor)

    authorized = engine.authorize(action, authorization)
    result = engine.execute(authorized)

    assert result.status == "succeeded"
    assert result.action_id == action.id
    assert len(executor.executed_actions) == 1
    assert executor.executed_actions[0].status == "executing"
    assert executor.executed_actions[0].authorization_id == authorization.id
