"""State transition rules for policy evaluations."""

from __future__ import annotations

from m3d.domain.common.transitions import can_transition as _can_transition
from m3d.domain.common.transitions import transition as _transition

POLICY_EVALUATION_STATES = frozenset(
    {
        "pending",
        "evaluated",
        "allowed",
        "denied",
        "approval_required",
    }
)


POLICY_EVALUATION_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending": frozenset({"evaluated"}),
    "evaluated": frozenset({"allowed", "denied", "approval_required"}),
    "allowed": frozenset(),
    "denied": frozenset(),
    "approval_required": frozenset(),
}


def can_transition(current: str, target: str) -> bool:
    """Return whether a policy evaluation state transition is allowed."""
    if current not in POLICY_EVALUATION_STATES:
        raise ValueError(f"Invalid current policy evaluation state: {current}")

    if target not in POLICY_EVALUATION_STATES:
        raise ValueError(f"Invalid target policy evaluation state: {target}")

    return _can_transition(
        current,
        target,
        POLICY_EVALUATION_TRANSITIONS,
    )


def transition(current: str, target: str) -> str:
    """Validate and return an allowed policy evaluation state transition."""
    if current not in POLICY_EVALUATION_STATES:
        raise ValueError(f"Invalid current policy evaluation state: {current}")

    if target not in POLICY_EVALUATION_STATES:
        raise ValueError(f"Invalid target policy evaluation state: {target}")

    try:
        return _transition(
            current,
            target,
            POLICY_EVALUATION_TRANSITIONS,
        )
    except ValueError as exc:
        raise ValueError(f"Invalid policy evaluation transition: {current} -> {target}") from exc
