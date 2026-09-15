"""State transition rules for operational policies."""

from __future__ import annotations

from m3d.domain.common.transitions import can_transition as _can_transition
from m3d.domain.common.transitions import transition as _transition
from m3d.domain.policy.policy import POLICY_STATES

POLICY_TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"active", "retired"}),
    "active": frozenset({"disabled", "retired"}),
    "disabled": frozenset({"active", "retired"}),
    "retired": frozenset(),
}


def can_transition(current: str, target: str) -> bool:
    """Return whether a policy state transition is allowed."""
    if current not in POLICY_STATES:
        raise ValueError(f"Invalid current policy state: {current}")

    if target not in POLICY_STATES:
        raise ValueError(f"Invalid target policy state: {target}")

    return _can_transition(current, target, POLICY_TRANSITIONS)


def transition(current: str, target: str) -> str:
    """Validate and return an allowed policy state transition."""
    if current not in POLICY_STATES:
        raise ValueError(f"Invalid current policy state: {current}")

    if target not in POLICY_STATES:
        raise ValueError(f"Invalid target policy state: {target}")

    try:
        return _transition(current, target, POLICY_TRANSITIONS)
    except ValueError as exc:
        raise ValueError(f"Invalid policy transition: {current} -> {target}") from exc
