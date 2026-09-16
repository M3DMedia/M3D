"""Port defining the contract for risk assessment."""

from __future__ import annotations

from abc import ABC, abstractmethod

from m3d.domain.decision import Decision
from m3d.domain.risk import Risk


class RiskAssessor(ABC):
    """Abstract interface for assessing the risk of an operational decision."""

    @abstractmethod
    def assess(self, decision: Decision) -> Risk:
        """Return a risk assessment for the supplied decision."""
        raise NotImplementedError
