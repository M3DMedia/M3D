"""Tests for the concrete verification engine."""

from __future__ import annotations

from m3d.domain.action import Action
from m3d.domain.action_result import ActionResult
from m3d.domain.common.types import (
    ActionId,
    DecisionId,
    EnvironmentId,
    VerificationId,
)
from m3d.domain.verification import Verification
from m3d.engines.verification import DefaultVerificationEngine
from m3d.ports.verification import Verifier


def make_action() -> Action:
    """Create a valid action."""
    return Action(
        id=ActionId("act_test"),
        decision_id=DecisionId("dec_test"),
        environment_id=EnvironmentId("env_test"),
        action_type="restart_service",
        description="Restart the affected service.",
    )


def make_result(action_id: ActionId | None = None) -> ActionResult:
    """Create a valid action result."""
    if action_id is None:
        action_id = ActionId("act_test")

    return ActionResult(
        id="result_test",
        action_id=action_id,
        status="succeeded",
    )


class FakeVerifier(Verifier):
    """Deterministic verifier for engine tests."""

    def __init__(self, verification: Verification) -> None:
        self.verification = verification
        self.verified_actions: list[tuple[Action, ActionResult]] = []

    def verify(
        self,
        action: Action,
        result: ActionResult,
    ) -> Verification:
        self.verified_actions.append((action, result))
        return self.verification


def make_verification(
    action_id: ActionId | None = None,
) -> Verification:
    """Create a valid verification."""
    if action_id is None:
        action_id = ActionId("act_test")

    return Verification(
        id=VerificationId("ver_test"),
        action_id=action_id,
        expected_outcome="The service is running normally.",
    )


def test_verify_returns_verifier_result() -> None:
    """The engine returns the verification produced by the verifier."""
    action = make_action()
    result = make_result()
    verification = make_verification()

    verifier = FakeVerifier(verification)
    engine = DefaultVerificationEngine(verifier)

    returned = engine.verify(action, result)

    assert returned == verification
    assert len(verifier.verified_actions) == 1
    assert verifier.verified_actions[0] == (action, result)


def test_verify_rejects_mismatched_action_result() -> None:
    """An action result belonging to another action is rejected."""
    action = make_action()
    result = make_result(ActionId("different_action"))

    verifier = FakeVerifier(make_verification())
    engine = DefaultVerificationEngine(verifier)

    try:
        engine.verify(action, result)
    except ValueError as exc:
        assert str(exc) == (f"Action result ID does not match action: {action.id}")
    else:
        raise AssertionError("Expected ValueError")

    assert verifier.verified_actions == []


def test_verify_rejects_mismatched_verification() -> None:
    """A verification belonging to another action is rejected."""
    action = make_action()
    result = make_result()
    verification = make_verification(ActionId("different_action"))

    verifier = FakeVerifier(verification)
    engine = DefaultVerificationEngine(verifier)

    try:
        engine.verify(action, result)
    except ValueError as exc:
        assert str(exc) == (f"Verification action ID does not match action: {action.id}")
    else:
        raise AssertionError("Expected ValueError")
