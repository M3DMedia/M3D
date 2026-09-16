"""Tests for the verification domain model and lifecycle."""

from __future__ import annotations

import pytest

from m3d.domain.common.types import ActionId, VerificationId
from m3d.domain.verification.verification import (
    VERIFICATION_STATES,
    Verification,
)


def make_verification(status: str = "pending") -> Verification:
    """Create a test verification."""
    return Verification(
        id=VerificationId("ver_test"),
        action_id=ActionId("act_test"),
        expected_outcome="The service is running normally.",
        status=status,
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("pending", "in_progress"),
        ("in_progress", "verified"),
        ("in_progress", "failed"),
        ("in_progress", "inconclusive"),
    ],
)
def test_valid_transitions(current: str, target: str) -> None:
    """Valid verification transitions are accepted."""
    verification = make_verification(current)

    transitioned = verification.transition_to(target)

    assert transitioned.status == target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("pending", "pending"),
        ("pending", "verified"),
        ("pending", "failed"),
        ("pending", "inconclusive"),
        ("in_progress", "pending"),
        ("in_progress", "in_progress"),
        ("verified", "pending"),
        ("verified", "in_progress"),
        ("verified", "failed"),
        ("verified", "inconclusive"),
        ("failed", "pending"),
        ("failed", "in_progress"),
        ("failed", "verified"),
        ("failed", "inconclusive"),
        ("inconclusive", "pending"),
        ("inconclusive", "in_progress"),
        ("inconclusive", "verified"),
        ("inconclusive", "failed"),
    ],
)
def test_invalid_transitions(current: str, target: str) -> None:
    """Invalid verification transitions are rejected."""
    verification = make_verification(current)

    with pytest.raises(ValueError, match="Invalid verification transition"):
        verification.transition_to(target)


@pytest.mark.parametrize("status", VERIFICATION_STATES)
def test_all_valid_states_are_accepted(status: str) -> None:
    """Every defined verification state is accepted."""
    verification = make_verification(status)

    assert verification.status == status


def test_unknown_state_is_rejected() -> None:
    """Unknown verification states are rejected."""
    with pytest.raises(ValueError, match="Invalid verification state"):
        make_verification("unknown")


def test_empty_id_is_rejected() -> None:
    """A verification requires an identifier."""
    with pytest.raises(ValueError, match="ID cannot be empty"):
        Verification(
            id=VerificationId(""),
            action_id=ActionId("act_test"),
            expected_outcome="The service is running normally.",
        )


def test_empty_expected_outcome_is_rejected() -> None:
    """A verification requires an expected outcome."""
    with pytest.raises(
        ValueError,
        match="Expected verification outcome cannot be empty",
    ):
        Verification(
            id=VerificationId("ver_test"),
            action_id=ActionId("act_test"),
            expected_outcome="",
        )


def test_observed_outcome_can_be_recorded() -> None:
    """An observed outcome can be recorded."""
    verification = Verification(
        id=VerificationId("ver_test"),
        action_id=ActionId("act_test"),
        expected_outcome="The service is running normally.",
        observed_outcome="The service is running normally.",
    )

    assert verification.observed_outcome == "The service is running normally."


def test_reason_can_be_recorded() -> None:
    """A verification reason can be recorded."""
    verification = Verification(
        id=VerificationId("ver_test"),
        action_id=ActionId("act_test"),
        expected_outcome="The service is running normally.",
        reason="Health check returned a successful response.",
    )

    assert verification.reason == "Health check returned a successful response."


def test_action_id_is_preserved() -> None:
    """Verification identifies the action being verified."""
    verification = make_verification()

    assert verification.action_id == ActionId("act_test")


def test_transition_returns_new_instance() -> None:
    """Verification transitions preserve immutability."""
    verification = make_verification()

    transitioned = verification.transition_to("in_progress")

    assert transitioned is not verification
    assert verification.status == "pending"
    assert transitioned.status == "in_progress"


def test_transition_preserves_identity() -> None:
    """A transition preserves verification identity."""
    verification = make_verification()

    transitioned = verification.transition_to("in_progress")

    assert transitioned.id == verification.id
    assert transitioned.action_id == verification.action_id
    assert transitioned.expected_outcome == verification.expected_outcome


def test_verification_is_immutable() -> None:
    """Verification instances cannot be mutated."""
    verification = make_verification()

    with pytest.raises(AttributeError):
        verification.status = "verified"  # type: ignore[misc]
