"""Tests for the action domain model and lifecycle."""

from __future__ import annotations

import pytest

from m3d.domain.action.action import ACTION_STATES, Action
from m3d.domain.common.types import (
    ActionId,
    AuthorizationId,
    DecisionId,
    EnvironmentId,
)


def make_action(status: str = "proposed") -> Action:
    """Create a test action."""
    return Action(
        id=ActionId("act_test"),
        decision_id=DecisionId("dec_test"),
        environment_id=EnvironmentId("env_test"),
        action_type="restart_service",
        description="Restart the affected service.",
        status=status,
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("proposed", "authorized"),
        ("proposed", "rejected"),
        ("proposed", "cancelled"),
        ("authorized", "executing"),
        ("authorized", "cancelled"),
        ("executing", "completed"),
        ("executing", "failed"),
        ("executing", "cancelled"),
        ("executing", "rolled_back"),
    ],
)
def test_valid_transitions(current: str, target: str) -> None:
    """Valid action transitions are accepted."""
    action = make_action(current)

    transitioned = action.transition_to(target)

    assert transitioned.status == target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("proposed", "proposed"),
        ("proposed", "executing"),
        ("proposed", "completed"),
        ("proposed", "failed"),
        ("proposed", "rolled_back"),
        ("authorized", "proposed"),
        ("authorized", "authorized"),
        ("authorized", "completed"),
        ("authorized", "failed"),
        ("authorized", "rolled_back"),
        ("executing", "proposed"),
        ("executing", "authorized"),
        ("executing", "executing"),
        ("completed", "proposed"),
        ("completed", "authorized"),
        ("completed", "executing"),
        ("completed", "failed"),
        ("completed", "rolled_back"),
        ("failed", "proposed"),
        ("failed", "authorized"),
        ("failed", "executing"),
        ("failed", "completed"),
        ("failed", "rolled_back"),
        ("rejected", "proposed"),
        ("rejected", "authorized"),
        ("rejected", "executing"),
        ("cancelled", "proposed"),
        ("cancelled", "authorized"),
        ("cancelled", "executing"),
        ("rolled_back", "proposed"),
        ("rolled_back", "authorized"),
        ("rolled_back", "executing"),
        ("rolled_back", "completed"),
    ],
)
def test_invalid_transitions(current: str, target: str) -> None:
    """Invalid action transitions are rejected."""
    action = make_action(current)

    with pytest.raises(ValueError, match="Invalid action transition"):
        action.transition_to(target)


@pytest.mark.parametrize("status", ACTION_STATES)
def test_all_valid_states_are_accepted(status: str) -> None:
    """Every defined action state is accepted."""
    action = make_action(status)

    assert action.status == status


def test_unknown_state_is_rejected() -> None:
    """Unknown action states are rejected."""
    with pytest.raises(ValueError, match="Invalid action state"):
        make_action("unknown")


def test_empty_id_is_rejected() -> None:
    """An action requires an identifier."""
    with pytest.raises(ValueError, match="ID cannot be empty"):
        Action(
            id=ActionId(""),
            decision_id=DecisionId("dec_test"),
            environment_id=EnvironmentId("env_test"),
            action_type="restart_service",
            description="Restart the affected service.",
        )


def test_empty_action_type_is_rejected() -> None:
    """An action requires an action type."""
    with pytest.raises(ValueError, match="Action type cannot be empty"):
        Action(
            id=ActionId("act_test"),
            decision_id=DecisionId("dec_test"),
            environment_id=EnvironmentId("env_test"),
            action_type="",
            description="Restart the affected service.",
        )


def test_empty_description_is_rejected() -> None:
    """An action requires a description."""
    with pytest.raises(ValueError, match="Action description cannot be empty"):
        Action(
            id=ActionId("act_test"),
            decision_id=DecisionId("dec_test"),
            environment_id=EnvironmentId("env_test"),
            action_type="restart_service",
            description="",
        )


def test_authorization_can_be_attached() -> None:
    """An authorization identifier can be associated with an action."""
    action = Action(
        id=ActionId("act_test"),
        decision_id=DecisionId("dec_test"),
        environment_id=EnvironmentId("env_test"),
        action_type="restart_service",
        description="Restart the affected service.",
        authorization_id=AuthorizationId("auth_test"),
    )

    assert action.authorization_id == AuthorizationId("auth_test")


def test_transition_returns_new_instance() -> None:
    """Action transitions preserve immutability."""
    action = make_action()

    transitioned = action.transition_to("authorized")

    assert transitioned is not action
    assert action.status == "proposed"
    assert transitioned.status == "authorized"


def test_transition_preserves_identity() -> None:
    """A transition preserves the action identity."""
    action = make_action()

    transitioned = action.transition_to("authorized")

    assert transitioned.id == action.id
    assert transitioned.decision_id == action.decision_id
    assert transitioned.environment_id == action.environment_id


def test_action_is_immutable() -> None:
    """Action instances cannot be mutated."""
    action = make_action()

    with pytest.raises(AttributeError):
        action.status = "authorized"  # type: ignore[misc]
