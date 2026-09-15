"""Port defining the contract for operational policy evaluation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from m3d.domain.decision import Decision
from m3d.domain.policy import Policy
from m3d.domain.policy_evaluation import PolicyEvaluation


class PolicyEngine(ABC):
    """Abstract interface for evaluating operational decisions against policies."""

    @abstractmethod
    def evaluate(
        self,
        decision: Decision,
        policies: Sequence[Policy],
    ) -> PolicyEvaluation:
        """Evaluate a decision against the applicable policies."""
        raise NotImplementedError
