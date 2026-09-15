"""Tests for operational hypothesis state transitions."""

import pytest

from m3d.domain.common.types import HypothesisId, InvestigationId
from m3d.domain.hypothesis import Hypothesis
from m3d.domain.hypothesis.transitions import can_transition, transition


def make_hypothesis(status: str = "proposed") -> Hypothesis:
    """Create a valid hypothesis for transition tests."""
    return Hypothesis(
        id=HypothesisId("hyp_test"),
        investigation_id=InvestigationId("inv_test"),
        statement="High disk utilization is caused by log growth.",
        status=status,
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("proposed", "testing"),
        ("testing", "supported"),
        ("testing", "weakened"),
        ("testing", "rejected"),
        ("supported", "confirmed"),
    ],
)
def test_allowed_transition_returns_true(current: str, target: str) -> None:
    """An allowed hypothesis transition returns True."""
    assert can_transition(current, target) is True


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("proposed", "supported"),
        ("proposed", "confirmed"),
        ("testing", "confirmed"),
        ("supported", "testing"),
        ("weakened", "testing"),
        ("rejected", "testing"),
        ("confirmed", "testing"),
    ],
)
def test_forbidden_transition_returns_false(current: str, target: str) -> None:
    """A forbidden hypothesis transition returns False."""
    assert can_transition(current, target) is False


def test_transition_returns_target_state() -> None:
    """A valid transition returns the target state."""
    assert transition("proposed", "testing") == "testing"


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("proposed", "confirmed"),
        ("testing", "confirmed"),
        ("supported", "testing"),
    ],
)
def test_forbidden_transition_raises_value_error(current: str, target: str) -> None:
    """A forbidden hypothesis transition raises ValueError."""
    with pytest.raises(ValueError, match="Invalid hypothesis transition"):
        transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("unknown", "testing"),
        ("proposed", "unknown"),
    ],
)
def test_unknown_state_raises_value_error(current: str, target: str) -> None:
    """An unknown hypothesis state raises ValueError."""
    with pytest.raises(ValueError, match="Invalid .* hypothesis state"):
        can_transition(current, target)


def test_model_transition_returns_new_hypothesis() -> None:
    """A model transition returns a new hypothesis with the target state."""
    hypothesis = make_hypothesis()

    transitioned = hypothesis.transition_to("testing")

    assert transitioned.status == "testing"
    assert hypothesis.status == "proposed"
    assert transitioned is not hypothesis


def test_model_transition_rejects_invalid_transition() -> None:
    """The model rejects transitions that violate the lifecycle."""
    hypothesis = make_hypothesis("testing")

    with pytest.raises(ValueError, match="Invalid hypothesis transition"):
        hypothesis.transition_to("confirmed")


def test_model_transition_preserves_identity() -> None:
    """A model transition preserves the hypothesis identity."""
    hypothesis = make_hypothesis()

    transitioned = hypothesis.transition_to("testing")

    assert transitioned.id == hypothesis.id
    assert transitioned.investigation_id == hypothesis.investigation_id
    assert transitioned.statement == hypothesis.statement


def test_model_is_immutable() -> None:
    """The frozen model cannot be mutated directly."""
    hypothesis = make_hypothesis()

    with pytest.raises(AttributeError):
        hypothesis.status = "testing"  # type: ignore[misc]
