"""Tests for the risk assessment port."""

from m3d.domain.common.types import DecisionId, InvestigationId, RiskId
from m3d.domain.decision import Decision
from m3d.domain.risk import Risk
from m3d.ports.risk_assessor import RiskAssessor


class FakeRiskAssessor(RiskAssessor):
    """Minimal risk assessor for contract tests."""

    def assess(self, decision: Decision) -> Risk:
        return Risk(
            id=RiskId("risk_test"),
            decision_id=decision.id,
            severity="medium",
            probability=0.5,
            impact="Potential service degradation.",
            reversibility="reversible",
        )


def make_decision() -> Decision:
    """Create a valid decision for contract tests."""
    return Decision(
        id=DecisionId("dec_test"),
        investigation_id=InvestigationId("inv_test"),
        decision="restart_service",
        rationale="The service is unavailable.",
    )


def test_risk_assessor_is_abstract() -> None:
    try:
        RiskAssessor()  # type: ignore[abstract]
    except TypeError:
        pass
    else:
        raise AssertionError("Expected TypeError")


def test_risk_assessor_implementation_returns_risk() -> None:
    assessor = FakeRiskAssessor()
    decision = make_decision()

    risk = assessor.assess(decision)

    assert risk.decision_id == decision.id
    assert risk.severity == "medium"
    assert risk.probability == 0.5
