"""Tests for the authorization domain model and lifecycle."""

from __future__ import annotations

import pytest

from m3d.domain.authorization.authorization import (
    AUTHORIZATION_STATES,
    Authorization,
)
from m3d.domain.common.types import ActionId, AuthorizationId


def make_authorization(status: str = "requested") -> Authorization:
    """Create a test authorization."""
    return Authorization(
        id=AuthorizationId("auth_test"),
        action_id=ActionId("act_test"),
        requested_by="operator",
        status=status,
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("requested", "granted"),
        ("requested", "denied"),
        ("requested", "expired"),
    ],
)
def test_valid_transitions(current: str, target: str) -> None:
    """Valid authorization transitions are accepted."""
    authorization = make_authorization(current)

    transitioned = authorization.transition_to(target)

    assert transitioned.status == target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("requested", "requested"),
        ("granted", "requested"),
        ("granted", "denied"),
        ("granted", "expired"),
        ("denied", "requested"),
        ("denied", "granted"),
        ("denied", "expired"),
        ("expired", "requested"),
        ("expired", "granted"),
        ("expired", "denied"),
    ],
)
def test_invalid_transitions(current: str, target: str) -> None:
    """Invalid authorization transitions are rejected."""
    authorization = make_authorization(current)

    with pytest.raises(ValueError, match="Invalid authorization transition"):
        authorization.transition_to(target)


@pytest.mark.parametrize("status", AUTHORIZATION_STATES)
def test_all_valid_states_are_accepted(status: str) -> None:
    """Every defined authorization state is accepted."""
    authorization = make_authorization(status)

    assert authorization.status == status


def test_unknown_state_is_rejected() -> None:
    """Unknown authorization states are rejected."""
    with pytest.raises(ValueError, match="Invalid authorization state"):
        make_authorization("unknown")


def test_empty_id_is_rejected() -> None:
    """An authorization requires an identifier."""
    with pytest.raises(ValueError, match="ID cannot be empty"):
        Authorization(
            id=AuthorizationId(""),
            action_id=ActionId("act_test"),
            requested_by="operator",
        )


def test_empty_requester_is_rejected() -> None:
    """An authorization requires a requester."""
    with pytest.raises(ValueError, match="requester cannot be empty"):
        Authorization(
            id=AuthorizationId("auth_test"),
            action_id=ActionId("act_test"),
            requested_by="",
        )


def test_transition_returns_new_instance() -> None:
    """Authorization transitions preserve immutability."""
    authorization = make_authorization()

    transitioned = authorization.transition_to("granted")

    assert transitioned is not authorization
    assert authorization.status == "requested"
    assert transitioned.status == "granted"


def test_transition_preserves_identity() -> None:
    """A transition preserves the authorization identity."""
    authorization = make_authorization()

    transitioned = authorization.transition_to("granted")

    assert transitioned.id == authorization.id
    assert transitioned.action_id == authorization.action_id
    assert transitioned.requested_by == authorization.requested_by


def test_authorization_is_immutable() -> None:
    """Authorization instances cannot be mutated."""
    authorization = make_authorization()

    with pytest.raises(AttributeError):
        authorization.status = "granted"  # type: ignore[misc]
