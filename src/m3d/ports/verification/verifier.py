"""Port defining the contract for operational outcome verification."""

from __future__ import annotations

from abc import ABC, abstractmethod

from m3d.domain.action import Action
from m3d.domain.action_result import ActionResult
from m3d.domain.verification import Verification


class Verifier(ABC):
    """Abstract interface for verifying operational action outcomes."""

    @abstractmethod
    def verify(
        self,
        action: Action,
        result: ActionResult,
    ) -> Verification:
        """Verify whether the action achieved its intended outcome."""
        raise NotImplementedError
