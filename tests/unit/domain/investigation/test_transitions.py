"""Tests for investigation state transition rules."""

import pytest

from m3d.domain.investigation.transitions import can_transition, transition


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("created", "scoping"),
        ("scoping", "collecting"),
        ("collecting", "analyzing"),
        ("analyzing", "hypothesis"),
        ("hypothesis", "testing"),
        ("testing", "hypothesis"),
        ("testing", "conclusion"),
        ("conclusion", "completed"),
    ],
)
def test_allowed_investigation_transitions(current: str, target: str) -> None:
    """Allowed investigation transitions return True."""
    assert can_transition(current, target) is True
    assert transition(current, target) == target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("created", "completed"),
        ("created", "testing"),
        ("scoping", "completed"),
        ("collecting", "hypothesis"),
        ("analyzing", "completed"),
        ("completed", "created"),
        ("failed", "created"),
        ("cancelled", "created"),
    ],
)
def test_forbidden_investigation_transitions(current: str, target: str) -> None:
    """Forbidden investigation transitions raise ValueError."""
    assert can_transition(current, target) is False

    with pytest.raises(ValueError, match="Invalid investigation transition"):
        transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("invalid", "created"),
        ("created", "invalid"),
    ],
)
def test_invalid_investigation_states_raise_value_error(
    current: str,
    target: str,
) -> None:
    """Unknown investigation states raise ValueError."""
    with pytest.raises(ValueError, match="Invalid .* investigation state"):
        can_transition(current, target)


from m3d.domain.common.types import EnvironmentId, InvestigationId
from m3d.domain.investigation import Investigation


def make_investigation() -> Investigation:
    """Create a deterministic investigation for transition tests."""
    return Investigation(
        id=InvestigationId("inv_test"),
        environment_id=EnvironmentId("env_test"),
        trigger="test.event",
        objective="Test investigation lifecycle",
    )


def test_investigation_transition_returns_new_instance() -> None:
    """A valid transition returns a new immutable investigation."""
    investigation = make_investigation()

    transitioned = investigation.transition_to("scoping")

    assert transitioned is not investigation
    assert investigation.status == "created"
    assert transitioned.status == "scoping"
    assert transitioned.id == investigation.id


def test_investigation_transition_rejects_invalid_transition() -> None:
    """An invalid transition raises ValueError without changing the original."""
    investigation = make_investigation()

    with pytest.raises(ValueError, match="Invalid investigation transition"):
        investigation.transition_to("completed")

    assert investigation.status == "created"
