"""In-memory implementation of the investigation persistence port."""

from __future__ import annotations

from m3d.domain.action import Action
from m3d.domain.action_result import ActionResult
from m3d.domain.authorization import Authorization
from m3d.domain.decision import Decision
from m3d.domain.evidence import Evidence
from m3d.domain.hypothesis import Hypothesis
from m3d.domain.investigation import Investigation
from m3d.domain.policy_evaluation import PolicyEvaluation
from m3d.domain.risk import Risk
from m3d.domain.verification import Verification
from m3d.ports.investigation import InvestigationStore


class InMemoryInvestigationStore(InvestigationStore):
    """Store investigation state in memory."""

    def __init__(self) -> None:
        self._investigations: dict[str, Investigation] = {}
        self._evidence: dict[str, Evidence] = {}
        self._hypotheses: dict[str, Hypothesis] = {}
        self._decisions: dict[str, Decision] = {}
        self._risks: dict[str, Risk] = {}
        self._policy_evaluations: dict[str, PolicyEvaluation] = {}
        self._authorizations: dict[str, Authorization] = {}
        self._actions: dict[str, Action] = {}
        self._action_results: dict[str, ActionResult] = {}
        self._verifications: dict[str, Verification] = {}

    def save_investigation(self, investigation: Investigation) -> None:
        self._investigations[investigation.id] = investigation

    def get_investigation(self, investigation_id: str) -> Investigation | None:
        return self._investigations.get(investigation_id)

    def save_evidence(self, evidence: Evidence) -> None:
        self._evidence[evidence.id] = evidence

    def get_evidence(self, investigation_id: str) -> list[Evidence]:
        return [
            item for item in self._evidence.values() if item.investigation_id == investigation_id
        ]

    def save_hypothesis(self, hypothesis: Hypothesis) -> None:
        self._hypotheses[hypothesis.id] = hypothesis

    def get_hypothesis(self, hypothesis_id: str) -> Hypothesis | None:
        return self._hypotheses.get(hypothesis_id)

    def get_hypotheses(self, investigation_id: str) -> list[Hypothesis]:
        return [
            item for item in self._hypotheses.values() if item.investigation_id == investigation_id
        ]

    def save_decision(self, decision: Decision) -> None:
        self._decisions[decision.id] = decision

    def get_decisions(self, investigation_id: str) -> list[Decision]:
        return [
            item for item in self._decisions.values() if item.investigation_id == investigation_id
        ]

    def save_risk(self, risk: Risk) -> None:
        self._risks[risk.id] = risk

    def get_risks(self, decision_id: str) -> list[Risk]:
        return [item for item in self._risks.values() if item.decision_id == decision_id]

    def save_policy_evaluation(self, evaluation: PolicyEvaluation) -> None:
        self._policy_evaluations[evaluation.id] = evaluation

    def get_policy_evaluations(self, decision_id: str) -> list[PolicyEvaluation]:
        return [
            item for item in self._policy_evaluations.values() if item.decision_id == decision_id
        ]

    def save_authorization(self, authorization: Authorization) -> None:
        self._authorizations[authorization.id] = authorization

    def get_authorization(self, authorization_id: str) -> Authorization | None:
        return self._authorizations.get(authorization_id)

    def save_action(self, action: Action) -> None:
        self._actions[action.id] = action

    def get_action(self, action_id: str) -> Action | None:
        return self._actions.get(action_id)

    def save_action_result(self, result: ActionResult) -> None:
        self._action_results[result.id] = result

    def get_action_result(self, action_id: str) -> ActionResult | None:
        results = [item for item in self._action_results.values() if item.action_id == action_id]
        return results[0] if results else None

    def save_verification(self, verification: Verification) -> None:
        self._verifications[verification.id] = verification

    def get_verification(self, action_id: str) -> Verification | None:
        verifications = [
            item for item in self._verifications.values() if item.action_id == action_id
        ]
        return verifications[0] if verifications else None
