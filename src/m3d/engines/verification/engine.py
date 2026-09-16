"""Verification orchestration engine."""

from __future__ import annotations

from m3d.domain.action import Action
from m3d.domain.action_result import ActionResult
from m3d.domain.verification import Verification
from m3d.ports.verification import Verifier


class DefaultVerificationEngine:
    """Orchestrate verification of operational action outcomes."""

    def __init__(self, verifier: Verifier) -> None:
        self._verifier = verifier

    def verify(
        self,
        action: Action,
        result: ActionResult,
    ) -> Verification:
        """Verify that an executed action achieved its intended outcome."""
        if result.action_id != action.id:
            raise ValueError(f"Action result ID does not match action: {action.id}")

        verification = self._verifier.verify(action, result)

        if verification.action_id != action.id:
            raise ValueError(f"Verification action ID does not match action: {action.id}")

        return verification
