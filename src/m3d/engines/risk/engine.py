"""Concrete operational risk assessment engine."""

from __future__ import annotations

from m3d.domain.decision import Decision
from m3d.domain.risk import Risk
from m3d.ports.risk import RiskEngine
from m3d.ports.risk_assessor import RiskAssessor


class DefaultRiskEngine(RiskEngine):
    """Delegate operational risk assessment to a risk assessor."""

    def __init__(self, assessor: RiskAssessor) -> None:
        self._assessor = assessor

    def assess(self, decision: Decision) -> Risk:
        """Assess the risk associated with a decision."""
        risk = self._assessor.assess(decision)

        if risk.decision_id != decision.id:
            raise ValueError(f"Risk decision ID does not match decision: {decision.id}")

        return risk
