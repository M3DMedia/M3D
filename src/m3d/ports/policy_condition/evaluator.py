"""Port defining the contract for policy condition evaluation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class PolicyConditionEvaluator(ABC):
    """Abstract interface for evaluating individual policy conditions."""

    @abstractmethod
    def evaluate(
        self,
        condition: str,
        context: Mapping[str, Any],
    ) -> bool:
        """Return whether a policy condition is satisfied by the context."""
        raise NotImplementedError
