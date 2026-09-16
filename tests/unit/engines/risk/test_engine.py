"""Tests for the concrete risk engine."""

from m3d.domain.common.types import DecisionId, InvestigationId, RiskId
from m3d.domain.decision import Decision
from m3d.domain.risk import Risk
from m3d.engines.risk import DefaultRiskEngine
from m3d.ports.risk_assessor import RiskAssessor


class FakeRiskAssessor(RiskAssessor):
    """Minimal risk assessor for engine tests."""

    def __init__(self, risk: Risk) -> None:
        self._risk = risk
        self.received_decision: Decision | None = None

    def assess(self, decision: Decision) -> Risk:
        self.received_decision = decision
        return self._risk


def make_decision() -> Decision:
    """Create a valid decision for tests."""
    return Decision(
        id=DecisionId("dec_test"),
        investigation_id=InvestigationId("inv_test"),
        decision="restart_service",
        rationale="The service is unavailable.",
    )


def make_risk(decision_id: DecisionId) -> Risk:
    """Create a valid risk assessment for tests."""
    return Risk(
        id=RiskId("risk_test"),
        decision_id=decision_id,
        severity="medium",
        probability=0.5,
        impact="Potential service degradation.",
        reversibility="reversible",
    )


def test_assess_delegates_to_assessor() -> None:
    decision = make_decision()
    risk = make_risk(decision.id)
    assessor = FakeRiskAssessor(risk)
    engine = DefaultRiskEngine(assessor)

    result = engine.assess(decision)

    assert result == risk
    assert assessor.received_decision == decision


def test_assess_rejects_mismatched_decision_id() -> None:
    decision = make_decision()
    risk = make_risk(DecisionId("different_decision"))
    assessor = FakeRiskAssessor(risk)
    engine = DefaultRiskEngine(assessor)

    try:
        engine.assess(decision)
    except ValueError as exc:
        assert str(exc) == "Risk decision ID does not match decision: dec_test"
    else:
        raise AssertionError("Expected ValueError")
