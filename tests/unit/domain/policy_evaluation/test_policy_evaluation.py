"""Tests for policy evaluation domain models."""

import pytest

from m3d.domain.common.types import DecisionId, PolicyId
from m3d.domain.policy_evaluation import PolicyEvaluation


def make_evaluation(status: str = "pending") -> PolicyEvaluation:
    """Create a valid policy evaluation for tests."""
    return PolicyEvaluation(
        id="pol_eval_test",
        decision_id=DecisionId("dec_test"),
        policy_id=PolicyId("pol_test"),
        status=status,
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("pending", "evaluated"),
        ("evaluated", "allowed"),
        ("evaluated", "denied"),
        ("evaluated", "approval_required"),
    ],
)
def test_allowed_transition(current: str, target: str) -> None:
    """An allowed transition returns the target state."""
    evaluation = make_evaluation(current)

    transitioned = evaluation.transition_to(target)

    assert transitioned.status == target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("pending", "allowed"),
        ("pending", "denied"),
        ("pending", "approval_required"),
        ("evaluated", "pending"),
        ("allowed", "evaluated"),
        ("allowed", "denied"),
        ("denied", "allowed"),
        ("approval_required", "allowed"),
    ],
)
def test_forbidden_transition_raises_value_error(
    current: str,
    target: str,
) -> None:
    """A forbidden transition raises ValueError."""
    evaluation = make_evaluation(current)

    with pytest.raises(
        ValueError,
        match="Invalid policy evaluation transition",
    ):
        evaluation.transition_to(target)


@pytest.mark.parametrize(
    "status",
    [
        "allowed",
        "denied",
        "approval_required",
    ],
)
def test_terminal_states_cannot_transition(status: str) -> None:
    """Policy evaluation outcome states are terminal."""
    evaluation = make_evaluation(status)

    with pytest.raises(
        ValueError,
        match="Invalid policy evaluation transition",
    ):
        evaluation.transition_to("evaluated")


@pytest.mark.parametrize(
    "status",
    [
        "pending",
        "evaluated",
        "allowed",
        "denied",
        "approval_required",
    ],
)
def test_valid_states_are_accepted(status: str) -> None:
    """Every defined policy evaluation state is accepted."""
    evaluation = make_evaluation(status)

    assert evaluation.status == status


def test_unknown_state_is_rejected() -> None:
    """An unknown policy evaluation state is rejected."""
    with pytest.raises(
        ValueError,
        match="Invalid policy evaluation state",
    ):
        make_evaluation("unknown")


def test_empty_id_is_rejected() -> None:
    """A policy evaluation requires an identifier."""
    with pytest.raises(ValueError, match="ID cannot be empty"):
        PolicyEvaluation(
            id="",
            decision_id=DecisionId("dec_test"),
            policy_id=PolicyId("pol_test"),
        )


def test_evaluated_status_allows_missing_result() -> None:
    """An evaluated policy evaluation may exist before its final result."""
    evaluation = make_evaluation("evaluated")

    assert evaluation.result is None


def test_evaluated_status_accepts_result() -> None:
    """An evaluated policy evaluation may contain its result."""
    evaluation = PolicyEvaluation(
        id="pol_eval_test",
        decision_id=DecisionId("dec_test"),
        policy_id=PolicyId("pol_test"),
        result="require_approval",
        reason="Production changes require human approval.",
        status="evaluated",
    )

    assert evaluation.result == "require_approval"
    assert evaluation.reason == "Production changes require human approval."


def test_transition_returns_new_instance() -> None:
    """A transition returns a new immutable model instance."""
    evaluation = make_evaluation()

    transitioned = evaluation.transition_to("evaluated")

    assert transitioned is not evaluation
    assert evaluation.status == "pending"
    assert transitioned.status == "evaluated"


def test_transition_preserves_identity() -> None:
    """A transition preserves decision and policy identity."""
    evaluation = make_evaluation()

    transitioned = evaluation.transition_to("evaluated")

    assert transitioned.id == evaluation.id
    assert transitioned.decision_id == evaluation.decision_id
    assert transitioned.policy_id == evaluation.policy_id


def test_model_is_immutable() -> None:
    """The frozen model cannot be mutated directly."""
    evaluation = make_evaluation()

    with pytest.raises(AttributeError):
        evaluation.status = "evaluated"  # type: ignore[misc]
