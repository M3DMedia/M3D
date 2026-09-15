"""Tests for operational risk state transitions."""

import pytest

from m3d.domain.common.types import DecisionId, RiskId
from m3d.domain.risk import Risk
from m3d.domain.risk.transitions import can_transition, transition


def make_risk(status: str = "assessed") -> Risk:
    """Create a valid risk assessment for transition tests."""
    return Risk(
        id=RiskId("risk_test"),
        decision_id=DecisionId("dec_test"),
        severity="high",
        probability=0.7,
        impact="Service interruption may affect dependent systems.",
        reversibility="partially reversible",
        affected_entities=("ent_test",),
        status=status,
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("assessed", "accepted"),
        ("assessed", "mitigated"),
        ("assessed", "escalated"),
        ("accepted", "mitigated"),
        ("accepted", "escalated"),
        ("escalated", "mitigated"),
    ],
)
def test_allowed_transition_returns_true(current: str, target: str) -> None:
    """An allowed risk transition returns True."""
    assert can_transition(current, target) is True


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("assessed", "assessed"),
        ("accepted", "assessed"),
        ("accepted", "accepted"),
        ("mitigated", "assessed"),
        ("mitigated", "accepted"),
        ("mitigated", "escalated"),
        ("escalated", "assessed"),
        ("escalated", "accepted"),
        ("escalated", "escalated"),
    ],
)
def test_forbidden_transition_returns_false(current: str, target: str) -> None:
    """A forbidden risk transition returns False."""
    assert can_transition(current, target) is False


def test_transition_returns_target_state() -> None:
    """A valid transition returns the target state."""
    assert transition("assessed", "accepted") == "accepted"


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("accepted", "assessed"),
        ("accepted", "accepted"),
        ("mitigated", "assessed"),
        ("escalated", "accepted"),
    ],
)
def test_forbidden_transition_raises_value_error(current: str, target: str) -> None:
    """A forbidden risk transition raises ValueError."""
    with pytest.raises(ValueError, match="Invalid risk transition"):
        transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("unknown", "accepted"),
        ("assessed", "unknown"),
    ],
)
def test_unknown_state_raises_value_error(current: str, target: str) -> None:
    """An unknown risk state raises ValueError."""
    with pytest.raises(ValueError, match="Invalid .* risk state"):
        can_transition(current, target)


def test_model_transition_returns_new_risk() -> None:
    """A model transition returns a new risk with the target state."""
    risk = make_risk()

    transitioned = risk.transition_to("accepted")

    assert transitioned.status == "accepted"
    assert risk.status == "assessed"
    assert transitioned is not risk


def test_model_transition_rejects_invalid_transition() -> None:
    """The model rejects transitions that violate the lifecycle."""
    risk = make_risk("accepted")

    with pytest.raises(ValueError, match="Invalid risk transition"):
        risk.transition_to("assessed")


def test_model_transition_preserves_identity() -> None:
    """A model transition preserves the risk identity."""
    risk = make_risk()

    transitioned = risk.transition_to("accepted")

    assert transitioned.id == risk.id
    assert transitioned.decision_id == risk.decision_id
    assert transitioned.severity == risk.severity


def test_model_is_immutable() -> None:
    """The frozen model cannot be mutated directly."""
    risk = make_risk()

    with pytest.raises(AttributeError):
        risk.status = "accepted"  # type: ignore[misc]
