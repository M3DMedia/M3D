"""State transition rules for operational risk assessments."""

from __future__ import annotations

from m3d.domain.common.transitions import can_transition as _can_transition
from m3d.domain.common.transitions import transition as _transition
from m3d.domain.risk.risk import RISK_STATES

RISK_TRANSITIONS: dict[str, frozenset[str]] = {
    "assessed": frozenset({"accepted", "mitigated", "escalated"}),
    "accepted": frozenset({"mitigated", "escalated"}),
    "mitigated": frozenset(),
    "escalated": frozenset({"mitigated"}),
}


def can_transition(current: str, target: str) -> bool:
    """Return whether a risk state transition is allowed."""
    if current not in RISK_STATES:
        raise ValueError(f"Invalid current risk state: {current}")

    if target not in RISK_STATES:
        raise ValueError(f"Invalid target risk state: {target}")

    return _can_transition(current, target, RISK_TRANSITIONS)


def transition(current: str, target: str) -> str:
    """Validate and return an allowed risk state transition."""
    if current not in RISK_STATES:
        raise ValueError(f"Invalid current risk state: {current}")

    if target not in RISK_STATES:
        raise ValueError(f"Invalid target risk state: {target}")

    try:
        return _transition(current, target, RISK_TRANSITIONS)
    except ValueError as exc:
        raise ValueError(f"Invalid risk transition: {current} -> {target}") from exc
