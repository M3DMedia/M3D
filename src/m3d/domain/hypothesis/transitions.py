"""State transition rules for operational hypotheses."""

from __future__ import annotations

from m3d.domain.common.transitions import can_transition as _can_transition
from m3d.domain.common.transitions import transition as _transition
from m3d.domain.hypothesis.hypothesis import HYPOTHESIS_STATES

HYPOTHESIS_TRANSITIONS: dict[str, frozenset[str]] = {
    "proposed": frozenset({"testing"}),
    "testing": frozenset({"supported", "weakened", "rejected"}),
    "supported": frozenset({"confirmed"}),
    "weakened": frozenset(),
    "rejected": frozenset(),
    "confirmed": frozenset(),
}


def can_transition(current: str, target: str) -> bool:
    """Return whether a hypothesis state transition is allowed."""
    if current not in HYPOTHESIS_STATES:
        raise ValueError(f"Invalid current hypothesis state: {current}")

    if target not in HYPOTHESIS_STATES:
        raise ValueError(f"Invalid target hypothesis state: {target}")

    return _can_transition(current, target, HYPOTHESIS_TRANSITIONS)


def transition(current: str, target: str) -> str:
    """Validate and return an allowed hypothesis state transition."""
    if current not in HYPOTHESIS_STATES:
        raise ValueError(f"Invalid current hypothesis state: {current}")

    if target not in HYPOTHESIS_STATES:
        raise ValueError(f"Invalid target hypothesis state: {target}")

    try:
        return _transition(current, target, HYPOTHESIS_TRANSITIONS)
    except ValueError as exc:
        raise ValueError(f"Invalid hypothesis transition: {current} -> {target}") from exc
