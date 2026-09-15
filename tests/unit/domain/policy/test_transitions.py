"""Tests for operational policy state transitions."""

import pytest

from m3d.domain.common.types import PolicyId
from m3d.domain.policy import Policy
from m3d.domain.policy.transitions import can_transition, transition


def make_policy(status: str = "draft") -> Policy:
    """Create a valid policy for transition tests."""
    return Policy(
        id=PolicyId("pol_test"),
        name="Protect production systems",
        description="Prevent unsafe operational changes.",
        scope="production",
        conditions=("environment == production", "risk.severity >= high"),
        effect="require_approval",
        priority=100,
        status=status,
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("draft", "active"),
        ("draft", "retired"),
        ("active", "disabled"),
        ("active", "retired"),
        ("disabled", "active"),
        ("disabled", "retired"),
    ],
)
def test_allowed_transition_returns_true(current: str, target: str) -> None:
    """An allowed policy transition returns True."""
    assert can_transition(current, target) is True


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("draft", "disabled"),
        ("active", "draft"),
        ("disabled", "draft"),
        ("disabled", "disabled"),
        ("retired", "draft"),
        ("retired", "active"),
        ("retired", "disabled"),
        ("retired", "retired"),
    ],
)
def test_forbidden_transition_returns_false(current: str, target: str) -> None:
    """A forbidden policy transition returns False."""
    assert can_transition(current, target) is False


def test_transition_returns_target_state() -> None:
    """A valid transition returns the target state."""
    assert transition("draft", "active") == "active"


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("draft", "disabled"),
        ("active", "draft"),
        ("disabled", "draft"),
        ("retired", "active"),
    ],
)
def test_forbidden_transition_raises_value_error(current: str, target: str) -> None:
    """A forbidden policy transition raises ValueError."""
    with pytest.raises(ValueError, match="Invalid policy transition"):
        transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("unknown", "active"),
        ("draft", "unknown"),
    ],
)
def test_unknown_state_raises_value_error(current: str, target: str) -> None:
    """An unknown policy state raises ValueError."""
    with pytest.raises(ValueError, match="Invalid .* policy state"):
        can_transition(current, target)


def test_model_transition_returns_new_policy() -> None:
    """A model transition returns a new policy with the target state."""
    policy = make_policy()

    transitioned = policy.transition_to("active")

    assert transitioned.status == "active"
    assert policy.status == "draft"
    assert transitioned is not policy


def test_model_transition_rejects_invalid_transition() -> None:
    """The model rejects transitions that violate the lifecycle."""
    policy = make_policy("retired")

    with pytest.raises(ValueError, match="Invalid policy transition"):
        policy.transition_to("active")


def test_model_transition_preserves_identity() -> None:
    """A model transition preserves the policy identity."""
    policy = make_policy()

    transitioned = policy.transition_to("active")

    assert transitioned.id == policy.id
    assert transitioned.name == policy.name
    assert transitioned.scope == policy.scope


def test_model_is_immutable() -> None:
    """The frozen model cannot be mutated directly."""
    policy = make_policy()

    with pytest.raises(AttributeError):
        policy.status = "active"  # type: ignore[misc]
