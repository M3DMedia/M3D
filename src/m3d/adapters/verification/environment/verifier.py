"""Environment-backed operational outcome verifier."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from m3d.domain.action import Action
from m3d.domain.action_result import ActionResult
from m3d.domain.common.types import VerificationId, new_id
from m3d.domain.verification import Verification
from m3d.ports.environment import EnvironmentPlugin
from m3d.ports.verification import Verifier


class EnvironmentVerifier(Verifier):
    """Verify an action outcome through an environment plugin."""

    def __init__(self, environment: EnvironmentPlugin) -> None:
        self._environment = environment

    def verify(
        self,
        action: Action,
        result: ActionResult,
    ) -> Verification:
        """Verify an action against the current environment state."""
        if result.action_id != action.id:
            raise ValueError(f"Action result ID does not match action: {action.id}")

        target, expected_outcome = self._verification_request(action)
        observation = self._environment.verify(target, expected_outcome)

        verified = observation.get("verified")
        if verified is not None and not isinstance(verified, bool):
            raise TypeError(
                "Environment verification result must contain a boolean or null 'verified' value."
            )

        status = self._verification_status(verified)
        observed_outcome = self._observed_outcome(observation)

        reason = observation.get("reason")
        if reason is not None and not isinstance(reason, str):
            raise TypeError("Environment verification reason must be a string.")

        return Verification(
            id=VerificationId(new_id("ver")),
            action_id=action.id,
            expected_outcome=expected_outcome,
            status=status,
            observed_outcome=observed_outcome,
            reason=reason,
            metadata={
                "verification_method": "environment",
                "target": target,
                "action_result_id": result.id,
                "environment_id": str(action.environment_id),
                "observation": dict(observation),
            },
        )

    def _verification_request(self, action: Action) -> tuple[str, str]:
        """Extract and validate verification details from action metadata."""
        raw_verification = action.metadata.get("verification")

        if not isinstance(raw_verification, Mapping):
            raise TypeError("Action verification metadata must be a mapping.")

        target = raw_verification.get("target")
        expected_outcome = raw_verification.get("expected_outcome")

        if not isinstance(target, str) or not target.strip():
            raise ValueError("Verification target must be a non-empty string.")

        if not isinstance(expected_outcome, str) or not expected_outcome.strip():
            raise ValueError("Verification expected_outcome must be a non-empty string.")

        return target, expected_outcome

    def _verification_status(self, verified: bool | None) -> str:
        """Map an environment verification result to a domain state."""
        if verified is True:
            return "verified"
        if verified is False:
            return "failed"
        return "inconclusive"

    def _observed_outcome(
        self,
        observation: Mapping[str, Any],
    ) -> str | None:
        """Extract the optional observed outcome from an environment result."""
        observed_outcome = observation.get("observed_outcome")

        if observed_outcome is None:
            return None

        if not isinstance(observed_outcome, str):
            raise TypeError("Environment verification observed_outcome must be a string.")

        return observed_outcome
