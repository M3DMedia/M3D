"""Port defining the contract for operational risk assessment."""

from __future__ import annotations

from abc import ABC, abstractmethod

from m3d.domain.decision import Decision
from m3d.domain.risk import Risk


class RiskEngine(ABC):
    """Abstract interface for assessing operational risk."""

    @abstractmethod
    def assess(self, decision: Decision) -> Risk:
        """Assess the potential risk associated with a decision."""
        raise NotImplementedError
