"""Tests for the environment-backed verification adapter."""

from __future__ import annotations

from typing import Any

import pytest

from m3d.adapters.verification.environment import EnvironmentVerifier
from m3d.domain.action import Action
from m3d.domain.action_result import ActionResult
from m3d.domain.common.types import ActionId, DecisionId, EnvironmentId
from m3d.ports.environment import EnvironmentPlugin


class FakeEnvironment(EnvironmentPlugin):
    """Deterministic environment for verifier tests."""

    def __init__(
        self,
        verification: dict[str, Any],
        environment_id: str = "env_test",
    ) -> None:
        self.environment_id = EnvironmentId(environment_id)
        self.verification = verification
        self.verify_calls: list[tuple[str, str]] = []

    def identify(self) -> EnvironmentId:
        return self.environment_id

    def discover(self) -> list[Any]:
        return []

    def observe(self) -> list[Any]:
        return []

    def collect(self, target: str) -> dict[str, Any]:
        return {"target": target}

    def execute(
        self,
        operation: str,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        return {"operation": operation, "parameters": parameters}

    def verify(
        self,
        target: str,
        expected_outcome: str,
    ) -> dict[str, Any]:
        self.verify_calls.append((target, expected_outcome))
        return self.verification


def make_action(
    metadata: dict[str, Any] | None = None,
) -> Action:
    """Create a valid action."""
    return Action(
        id=ActionId("act_test"),
        decision_id=DecisionId("dec_test"),
        environment_id=EnvironmentId("env_test"),
        action_type="restart_service",
        description="Restart the affected service.",
        metadata=metadata
        if metadata is not None
        else {
            "verification": {
                "target": "service:nginx",
                "expected_outcome": "Service is running.",
            }
        },
    )


def make_result(
    action_id: ActionId | None = None,
) -> ActionResult:
    """Create a valid action result."""
    if action_id is None:
        action_id = ActionId("act_test")

    return ActionResult(
        id="result_test",
        action_id=action_id,
        status="succeeded",
    )


def test_verified_environment_result_creates_verified_verification() -> None:
    """A positive environment result produces a verified verification."""
    environment = FakeEnvironment(
        {
            "verified": True,
            "observed_outcome": "Service is running.",
            "reason": "Health check succeeded.",
        }
    )
    verifier = EnvironmentVerifier(environment)

    verification = verifier.verify(make_action(), make_result())

    assert verification.status == "verified"
    assert verification.expected_outcome == "Service is running."
    assert verification.observed_outcome == "Service is running."
    assert verification.reason == "Health check succeeded."
    assert verification.action_id == ActionId("act_test")
    assert verification.metadata["verification_method"] == "environment"
    assert verification.metadata["target"] == "service:nginx"
    assert verification.metadata["action_result_id"] == "result_test"
    assert environment.verify_calls == [("service:nginx", "Service is running.")]


def test_failed_environment_result_creates_failed_verification() -> None:
    """A negative environment result produces a failed verification."""
    environment = FakeEnvironment(
        {
            "verified": False,
            "observed_outcome": "Service remains stopped.",
            "reason": "Health check failed.",
        }
    )
    verifier = EnvironmentVerifier(environment)

    verification = verifier.verify(make_action(), make_result())

    assert verification.status == "failed"
    assert verification.observed_outcome == "Service remains stopped."
    assert verification.reason == "Health check failed."


def test_unknown_environment_result_creates_inconclusive_verification() -> None:
    """An indeterminate environment result produces an inconclusive verification."""
    environment = FakeEnvironment(
        {
            "verified": None,
            "observed_outcome": "Service state could not be determined.",
        }
    )
    verifier = EnvironmentVerifier(environment)

    verification = verifier.verify(make_action(), make_result())

    assert verification.status == "inconclusive"
    assert verification.observed_outcome == "Service state could not be determined."
    assert verification.reason is None


def test_action_result_mismatch_is_rejected() -> None:
    """A result belonging to another action is rejected."""
    environment = FakeEnvironment({"verified": True})
    verifier = EnvironmentVerifier(environment)

    with pytest.raises(
        ValueError,
        match="Action result ID does not match action",
    ):
        verifier.verify(
            make_action(),
            make_result(ActionId("different_action")),
        )

    assert environment.verify_calls == []


def test_missing_verification_metadata_is_rejected() -> None:
    """Verification metadata is required."""
    environment = FakeEnvironment({"verified": True})
    verifier = EnvironmentVerifier(environment)

    action = make_action(metadata={})

    with pytest.raises(
        TypeError,
        match="Action verification metadata must be a mapping",
    ):
        verifier.verify(action, make_result())


@pytest.mark.parametrize(
    "verification_metadata",
    [
        {"target": "service:nginx"},
        {"expected_outcome": "Service is running."},
        {
            "target": "",
            "expected_outcome": "Service is running.",
        },
        {
            "target": "service:nginx",
            "expected_outcome": "",
        },
    ],
)
def test_invalid_verification_metadata_is_rejected(
    verification_metadata: dict[str, Any],
) -> None:
    """Incomplete verification metadata is rejected."""
    environment = FakeEnvironment({"verified": True})
    verifier = EnvironmentVerifier(environment)

    action = make_action(
        metadata={"verification": verification_metadata},
    )

    with pytest.raises(ValueError):
        verifier.verify(action, make_result())


@pytest.mark.parametrize("verified", ["yes", 1, 0, []])
def test_invalid_verified_value_is_rejected(verified: Any) -> None:
    """Environment verification requires a boolean or null result."""
    environment = FakeEnvironment({"verified": verified})
    verifier = EnvironmentVerifier(environment)

    with pytest.raises(
        TypeError,
        match="boolean or null 'verified'",
    ):
        verifier.verify(make_action(), make_result())


def test_invalid_observed_outcome_is_rejected() -> None:
    """An observed outcome must be a string when supplied."""
    environment = FakeEnvironment(
        {
            "verified": True,
            "observed_outcome": {"status": "running"},
        }
    )
    verifier = EnvironmentVerifier(environment)

    with pytest.raises(
        TypeError,
        match="observed_outcome must be a string",
    ):
        verifier.verify(make_action(), make_result())


def test_invalid_reason_is_rejected() -> None:
    """A verification reason must be a string when supplied."""
    environment = FakeEnvironment(
        {
            "verified": True,
            "reason": {"message": "Health check succeeded."},
        }
    )
    verifier = EnvironmentVerifier(environment)

    with pytest.raises(
        TypeError,
        match="verification reason must be a string",
    ):
        verifier.verify(make_action(), make_result())


def test_observation_is_preserved_in_metadata() -> None:
    """The raw environment observation is preserved for auditability."""
    observation = {
        "verified": True,
        "observed_outcome": "Service is running.",
        "details": {
            "process": "nginx",
            "pid": 1234,
        },
    }
    environment = FakeEnvironment(observation)
    verifier = EnvironmentVerifier(environment)

    verification = verifier.verify(make_action(), make_result())

    assert verification.metadata["observation"] == observation
