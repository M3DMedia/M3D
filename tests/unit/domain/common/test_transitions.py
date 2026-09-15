"""Tests for generic domain state transition utilities."""

import pytest

from m3d.domain.common.transitions import can_transition, transition

TRANSITIONS = {
    "created": {"active", "cancelled"},
    "active": {"completed", "failed"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
}


def test_allowed_transition_returns_true() -> None:
    """An allowed transition returns True."""
    assert can_transition("created", "active", TRANSITIONS) is True


def test_forbidden_transition_returns_false() -> None:
    """A forbidden transition returns False."""
    assert can_transition("created", "completed", TRANSITIONS) is False


def test_transition_returns_target_state() -> None:
    """A valid transition returns the target state."""
    assert transition("created", "active", TRANSITIONS) == "active"


def test_forbidden_transition_raises_value_error() -> None:
    """A forbidden transition raises ValueError."""
    with pytest.raises(ValueError, match="Invalid state transition"):
        transition("created", "completed", TRANSITIONS)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("unknown", "active"),
        ("created", "unknown"),
    ],
)
def test_unknown_state_raises_value_error(current: str, target: str) -> None:
    """An unknown state raises ValueError."""
    with pytest.raises(ValueError, match="Invalid .* state"):
        can_transition(current, target, TRANSITIONS)
