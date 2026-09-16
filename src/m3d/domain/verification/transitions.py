"""State transition rules for operational verification."""

from __future__ import annotations

from m3d.domain.common.transitions import can_transition as _can_transition
from m3d.domain.common.transitions import transition as _transition
from m3d.domain.verification.verification import VERIFICATION_STATES

VERIFICATION_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending": frozenset({"in_progress"}),
    "in_progress": frozenset(
        {
            "verified",
            "failed",
            "inconclusive",
        }
    ),
    "verified": frozenset(),
    "failed": frozenset(),
    "inconclusive": frozenset(),
}


def can_transition(current: str, target: str) -> bool:
    """Return whether a verification state transition is allowed."""
    if current not in VERIFICATION_STATES:
        raise ValueError(f"Invalid current verification state: {current}")

    if target not in VERIFICATION_STATES:
        raise ValueError(f"Invalid target verification state: {target}")

    return _can_transition(current, target, VERIFICATION_TRANSITIONS)


def transition(current: str, target: str) -> str:
    """Validate and return an allowed verification state transition."""
    if current not in VERIFICATION_STATES:
        raise ValueError(f"Invalid current verification state: {current}")

    if target not in VERIFICATION_STATES:
        raise ValueError(f"Invalid target verification state: {target}")

    try:
        return _transition(current, target, VERIFICATION_TRANSITIONS)
    except ValueError as exc:
        raise ValueError(f"Invalid verification transition: {current} -> {target}") from exc
