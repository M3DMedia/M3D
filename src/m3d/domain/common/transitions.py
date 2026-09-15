"""Generic state transition utilities for the M3D domain."""

from __future__ import annotations

from collections.abc import Collection, Mapping


def can_transition(
    current: str,
    target: str,
    transitions: Mapping[str, Collection[str]],
) -> bool:
    """Return whether a state transition is allowed."""
    if current not in transitions:
        raise ValueError(f"Invalid current state: {current}")

    if target not in transitions:
        raise ValueError(f"Invalid target state: {target}")

    return target in transitions[current]


def transition(
    current: str,
    target: str,
    transitions: Mapping[str, Collection[str]],
) -> str:
    """Validate and return an allowed state transition."""
    if not can_transition(current, target, transitions):
        raise ValueError(f"Invalid state transition: {current} -> {target}")

    return target
