"""Tests for the in-memory investigation store."""

from datetime import UTC, datetime

from m3d.adapters.storage.memory import InMemoryInvestigationStore
from m3d.domain.action import Action
from m3d.domain.action_result import ActionResult
from m3d.domain.authorization import Authorization
from m3d.domain.common.types import (
    ActionId,
    AuthorizationId,
    DecisionId,
    EnvironmentId,
    EvidenceId,
    HypothesisId,
    InvestigationId,
    PolicyId,
    RiskId,
    VerificationId,
)
from m3d.domain.decision import Decision
from m3d.domain.evidence import Evidence
from m3d.domain.hypothesis import Hypothesis
from m3d.domain.investigation import Investigation
from m3d.domain.policy_evaluation import PolicyEvaluation
from m3d.domain.risk import Risk
from m3d.domain.verification import Verification

TIMESTAMP = datetime(2026, 1, 1, tzinfo=UTC)
ENVIRONMENT_ID = EnvironmentId("env_test")


def make_investigation(
    investigation_id: str = "inv_test",
) -> Investigation:
    return Investigation(
        id=InvestigationId(investigation_id),
        environment_id=ENVIRONMENT_ID,
        trigger="test",
        objective="Test investigation",
    )


def test_save_and_get_investigation() -> None:
    store = InMemoryInvestigationStore()
    investigation = make_investigation()

    store.save_investigation(investigation)

    assert store.get_investigation(investigation.id) == investigation


def test_get_missing_investigation_returns_none() -> None:
    store = InMemoryInvestigationStore()

    assert store.get_investigation("missing") is None


def test_save_and_get_evidence_by_investigation() -> None:
    store = InMemoryInvestigationStore()
    evidence = Evidence(
        id=EvidenceId("evidence_test"),
        investigation_id=InvestigationId("inv_test"),
        source="test",
        observation="CPU usage is elevated",
        collected_at=TIMESTAMP,
        collection_method="test",
    )

    store.save_evidence(evidence)

    assert store.get_evidence("inv_test") == [evidence]


def test_evidence_query_excludes_other_investigations() -> None:
    store = InMemoryInvestigationStore()
    evidence = Evidence(
        id=EvidenceId("evidence_other"),
        investigation_id=InvestigationId("inv_other"),
        source="test",
        observation="Unrelated observation",
        collected_at=TIMESTAMP,
        collection_method="test",
    )

    store.save_evidence(evidence)

    assert store.get_evidence("inv_test") == []


def test_save_and_get_hypotheses_by_investigation() -> None:
    store = InMemoryInvestigationStore()
    hypothesis = Hypothesis(
        id=HypothesisId("hypothesis_test"),
        investigation_id=InvestigationId("inv_test"),
        statement="A process is consuming excessive CPU.",
    )

    store.save_hypothesis(hypothesis)

    assert store.get_hypotheses("inv_test") == [hypothesis]


def test_save_and_get_decisions_by_investigation() -> None:
    store = InMemoryInvestigationStore()
    decision = Decision(
        id=DecisionId("decision_test"),
        investigation_id=InvestigationId("inv_test"),
        decision="Investigate the highest CPU process.",
        rationale="It is the leading observed anomaly.",
    )

    store.save_decision(decision)

    assert store.get_decisions("inv_test") == [decision]


def test_get_decision_by_id() -> None:
    store = InMemoryInvestigationStore()
    decision = Decision(
        id=DecisionId("decision_test"),
        investigation_id=InvestigationId("inv_test"),
        decision="Investigate the highest CPU process.",
        rationale="It is the leading observed anomaly.",
    )
    store.save_decision(decision)
    assert store.get_decision("decision_test") == decision


def test_get_missing_decision_returns_none() -> None:
    store = InMemoryInvestigationStore()
    assert store.get_decision("missing") is None


def test_save_and_get_risks_by_decision() -> None:
    store = InMemoryInvestigationStore()
    risk = Risk(
        id=RiskId("risk_test"),
        decision_id=DecisionId("decision_test"),
        severity="medium",
        probability=0.5,
        impact="Service degradation",
        reversibility="reversible",
    )

    store.save_risk(risk)

    assert store.get_risks("decision_test") == [risk]


def test_save_and_get_policy_evaluations_by_decision() -> None:
    store = InMemoryInvestigationStore()
    evaluation = PolicyEvaluation(
        id="evaluation_test",
        decision_id=DecisionId("decision_test"),
        policy_id=PolicyId("policy_test"),
    )

    store.save_policy_evaluation(evaluation)

    assert store.get_policy_evaluations("decision_test") == [evaluation]


def test_save_and_get_authorization() -> None:
    store = InMemoryInvestigationStore()
    authorization = Authorization(
        id=AuthorizationId("authorization_test"),
        action_id=ActionId("action_test"),
        requested_by="test",
    )

    store.save_authorization(authorization)

    assert store.get_authorization(authorization.id) == authorization


def test_get_missing_authorization_returns_none() -> None:
    store = InMemoryInvestigationStore()

    assert store.get_authorization("missing") is None


def test_save_and_get_action() -> None:
    store = InMemoryInvestigationStore()
    action = Action(
        id=ActionId("action_test"),
        decision_id=DecisionId("decision_test"),
        environment_id=ENVIRONMENT_ID,
        action_type="restart_service",
        description="Restart the affected service.",
    )

    store.save_action(action)

    assert store.get_action(action.id) == action


def test_get_missing_action_returns_none() -> None:
    store = InMemoryInvestigationStore()

    assert store.get_action("missing") is None


def test_save_and_get_action_result() -> None:
    store = InMemoryInvestigationStore()
    result = ActionResult(
        id="result_test",
        action_id=ActionId("action_test"),
        status="succeeded",
        output="Service restarted.",
    )

    store.save_action_result(result)

    assert store.get_action_result("action_test") == result


def test_get_missing_action_result_returns_none() -> None:
    store = InMemoryInvestigationStore()

    assert store.get_action_result("missing") is None


def test_save_and_get_verification() -> None:
    store = InMemoryInvestigationStore()
    verification = Verification(
        id=VerificationId("verification_test"),
        action_id=ActionId("action_test"),
        expected_outcome="Service is running.",
    )

    store.save_verification(verification)

    assert store.get_verification("action_test") == verification


def test_get_missing_verification_returns_none() -> None:
    store = InMemoryInvestigationStore()

    assert store.get_verification("missing") is None


def test_saving_same_id_replaces_existing_record() -> None:
    store = InMemoryInvestigationStore()
    original = make_investigation()
    replacement = make_investigation()
    replacement = Investigation(
        id=original.id,
        environment_id=ENVIRONMENT_ID,
        trigger="replacement",
        objective="Replacement investigation",
    )

    store.save_investigation(original)
    store.save_investigation(replacement)

    assert store.get_investigation(original.id) == replacement
