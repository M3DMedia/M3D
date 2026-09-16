"""State transition rules for operational actions."""

from __future__ import annotations

from m3d.domain.action.action import ACTION_STATES
from m3d.domain.common.transitions import can_transition as _can_transition
from m3d.domain.common.transitions import transition as _transition

ACTION_TRANSITIONS: dict[str, frozenset[str]] = {
    "proposed": frozenset({"authorized", "rejected", "cancelled"}),
    "authorized": frozenset({"executing", "cancelled"}),
    "executing": frozenset(
        {
            "completed",
            "failed",
            "cancelled",
            "rolled_back",
        }
    ),
    "completed": frozenset(),
    "failed": frozenset(),
    "rejected": frozenset(),
    "cancelled": frozenset(),
    "rolled_back": frozenset(),
}


def can_transition(current: str, target: str) -> bool:
    """Return whether an action state transition is allowed."""
    if current not in ACTION_STATES:
        raise ValueError(f"Invalid current action state: {current}")

    if target not in ACTION_STATES:
        raise ValueError(f"Invalid target action state: {target}")

    return _can_transition(current, target, ACTION_TRANSITIONS)


def transition(current: str, target: str) -> str:
    """Validate and return an allowed action state transition."""
    if current not in ACTION_STATES:
        raise ValueError(f"Invalid current action state: {current}")

    if target not in ACTION_STATES:
        raise ValueError(f"Invalid target action state: {target}")

    try:
        return _transition(current, target, ACTION_TRANSITIONS)
    except ValueError as exc:
        raise ValueError(f"Invalid action transition: {current} -> {target}") from exc
