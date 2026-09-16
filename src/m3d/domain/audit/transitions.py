"""State transition rules for immutable audit records."""

from __future__ import annotations

from m3d.domain.audit.audit import AUDIT_STATES
from m3d.domain.common.transitions import can_transition as _can_transition
from m3d.domain.common.transitions import transition as _transition

AUDIT_TRANSITIONS: dict[str, frozenset[str]] = {
    "created": frozenset({"sealed"}),
    "sealed": frozenset(),
}


def can_transition(current: str, target: str) -> bool:
    """Return whether an audit state transition is allowed."""
    if current not in AUDIT_STATES:
        raise ValueError(f"Invalid current audit state: {current}")

    if target not in AUDIT_STATES:
        raise ValueError(f"Invalid target audit state: {target}")

    return _can_transition(current, target, AUDIT_TRANSITIONS)


def transition(current: str, target: str) -> str:
    """Validate and return an allowed audit state transition."""
    if current not in AUDIT_STATES:
        raise ValueError(f"Invalid current audit state: {current}")

    if target not in AUDIT_STATES:
        raise ValueError(f"Invalid target audit state: {target}")

    try:
        return _transition(current, target, AUDIT_TRANSITIONS)
    except ValueError as exc:
        raise ValueError(f"Invalid audit transition: {current} -> {target}") from exc
