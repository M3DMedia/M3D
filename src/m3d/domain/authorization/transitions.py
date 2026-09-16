"""State transition rules for operational authorizations."""

from __future__ import annotations

from m3d.domain.authorization.authorization import AUTHORIZATION_STATES
from m3d.domain.common.transitions import can_transition as _can_transition
from m3d.domain.common.transitions import transition as _transition

AUTHORIZATION_TRANSITIONS: dict[str, frozenset[str]] = {
    "requested": frozenset({"granted", "denied", "expired"}),
    "granted": frozenset(),
    "denied": frozenset(),
    "expired": frozenset(),
}


def can_transition(current: str, target: str) -> bool:
    """Return whether an authorization state transition is allowed."""
    if current not in AUTHORIZATION_STATES:
        raise ValueError(f"Invalid current authorization state: {current}")

    if target not in AUTHORIZATION_STATES:
        raise ValueError(f"Invalid target authorization state: {target}")

    return _can_transition(current, target, AUTHORIZATION_TRANSITIONS)


def transition(current: str, target: str) -> str:
    """Validate and return an allowed authorization state transition."""
    if current not in AUTHORIZATION_STATES:
        raise ValueError(f"Invalid current authorization state: {current}")

    if target not in AUTHORIZATION_STATES:
        raise ValueError(f"Invalid target authorization state: {target}")

    try:
        return _transition(current, target, AUTHORIZATION_TRANSITIONS)
    except ValueError as exc:
        raise ValueError(f"Invalid authorization transition: {current} -> {target}") from exc
