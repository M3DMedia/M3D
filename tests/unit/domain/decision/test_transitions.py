"""Tests for operational decision state transitions."""

import pytest

from m3d.domain.common.types import DecisionId, EvidenceId, InvestigationId
from m3d.domain.decision import Decision
from m3d.domain.decision.transitions import can_transition, transition


def make_decision(status: str = "proposed") -> Decision:
    """Create a valid decision for transition tests."""
    return Decision(
        id=DecisionId("dec_test"),
        investigation_id=InvestigationId("inv_test"),
        decision="Clean up excessive log files.",
        rationale="Evidence shows log growth is consuming available disk space.",
        evidence_ids=(EvidenceId("evd_test"),),
        confidence=0.9,
        status=status,
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("proposed", "evaluated"),
        ("proposed", "rejected"),
        ("evaluated", "accepted"),
        ("evaluated", "rejected"),
        ("accepted", "superseded"),
    ],
)
def test_allowed_transition_returns_true(current: str, target: str) -> None:
    """An allowed decision transition returns True."""
    assert can_transition(current, target) is True


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("proposed", "accepted"),
        ("proposed", "superseded"),
        ("evaluated", "superseded"),
        ("accepted", "proposed"),
        ("accepted", "rejected"),
        ("rejected", "evaluated"),
        ("rejected", "accepted"),
        ("superseded", "accepted"),
    ],
)
def test_forbidden_transition_returns_false(current: str, target: str) -> None:
    """A forbidden decision transition returns False."""
    assert can_transition(current, target) is False


def test_transition_returns_target_state() -> None:
    """A valid transition returns the target state."""
    assert transition("proposed", "evaluated") == "evaluated"


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("proposed", "accepted"),
        ("proposed", "superseded"),
        ("evaluated", "superseded"),
        ("accepted", "rejected"),
    ],
)
def test_forbidden_transition_raises_value_error(current: str, target: str) -> None:
    """A forbidden decision transition raises ValueError."""
    with pytest.raises(ValueError, match="Invalid decision transition"):
        transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("unknown", "evaluated"),
        ("proposed", "unknown"),
    ],
)
def test_unknown_state_raises_value_error(current: str, target: str) -> None:
    """An unknown decision state raises ValueError."""
    with pytest.raises(ValueError, match="Invalid .* decision state"):
        can_transition(current, target)


def test_model_transition_returns_new_decision() -> None:
    """A model transition returns a new decision with the target state."""
    decision = make_decision()

    transitioned = decision.transition_to("evaluated")

    assert transitioned.status == "evaluated"
    assert decision.status == "proposed"
    assert transitioned is not decision


def test_model_transition_rejects_invalid_transition() -> None:
    """The model rejects transitions that violate the lifecycle."""
    decision = make_decision("proposed")

    with pytest.raises(ValueError, match="Invalid decision transition"):
        decision.transition_to("accepted")


def test_model_transition_preserves_identity() -> None:
    """A model transition preserves the decision identity."""
    decision = make_decision()

    transitioned = decision.transition_to("evaluated")

    assert transitioned.id == decision.id
    assert transitioned.investigation_id == decision.investigation_id
    assert transitioned.decision == decision.decision


def test_model_is_immutable() -> None:
    """The frozen model cannot be mutated directly."""
    decision = make_decision()

    with pytest.raises(AttributeError):
        decision.status = "evaluated"  # type: ignore[misc]
