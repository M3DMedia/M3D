"""State transition rules for operational investigations."""

from __future__ import annotations

from m3d.domain.common.transitions import can_transition as _can_transition
from m3d.domain.common.transitions import transition as _transition
from m3d.domain.investigation.investigation import INVESTIGATION_STATES

INVESTIGATION_TRANSITIONS: dict[str, frozenset[str]] = {
    "created": frozenset({"scoping", "failed", "cancelled"}),
    "scoping": frozenset({"collecting", "failed", "cancelled"}),
    "collecting": frozenset({"analyzing", "failed", "cancelled"}),
    "analyzing": frozenset({"hypothesis", "failed", "cancelled"}),
    "hypothesis": frozenset({"testing", "conclusion", "failed", "cancelled"}),
    "testing": frozenset(
        {
            "hypothesis",
            "conclusion",
            "failed",
            "cancelled",
        }
    ),
    "conclusion": frozenset({"completed", "failed", "cancelled"}),
    "completed": frozenset(),
    "failed": frozenset(),
    "cancelled": frozenset(),
}


def can_transition(current: str, target: str) -> bool:
    """Return whether an investigation state transition is allowed."""
    if current not in INVESTIGATION_STATES:
        raise ValueError(f"Invalid current investigation state: {current}")

    if target not in INVESTIGATION_STATES:
        raise ValueError(f"Invalid target investigation state: {target}")

    return _can_transition(current, target, INVESTIGATION_TRANSITIONS)


def transition(current: str, target: str) -> str:
    """Validate and return an allowed investigation state transition."""
    if current not in INVESTIGATION_STATES:
        raise ValueError(f"Invalid current investigation state: {current}")

    if target not in INVESTIGATION_STATES:
        raise ValueError(f"Invalid target investigation state: {target}")

    try:
        return _transition(current, target, INVESTIGATION_TRANSITIONS)
    except ValueError as exc:
        raise ValueError(f"Invalid investigation transition: {current} -> {target}") from exc
