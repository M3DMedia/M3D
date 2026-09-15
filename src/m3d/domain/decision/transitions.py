"""State transition rules for operational decisions."""

from __future__ import annotations

from m3d.domain.common.transitions import can_transition as _can_transition
from m3d.domain.common.transitions import transition as _transition
from m3d.domain.decision.decision import DECISION_STATES

DECISION_TRANSITIONS: dict[str, frozenset[str]] = {
    "proposed": frozenset({"evaluated", "rejected"}),
    "evaluated": frozenset({"accepted", "rejected"}),
    "accepted": frozenset({"superseded"}),
    "rejected": frozenset(),
    "superseded": frozenset(),
}


def can_transition(current: str, target: str) -> bool:
    """Return whether a decision state transition is allowed."""
    if current not in DECISION_STATES:
        raise ValueError(f"Invalid current decision state: {current}")

    if target not in DECISION_STATES:
        raise ValueError(f"Invalid target decision state: {target}")

    return _can_transition(current, target, DECISION_TRANSITIONS)


def transition(current: str, target: str) -> str:
    """Validate and return an allowed decision state transition."""
    if current not in DECISION_STATES:
        raise ValueError(f"Invalid current decision state: {current}")

    if target not in DECISION_STATES:
        raise ValueError(f"Invalid target decision state: {target}")

    try:
        return _transition(current, target, DECISION_TRANSITIONS)
    except ValueError as exc:
        raise ValueError(f"Invalid decision transition: {current} -> {target}") from exc
