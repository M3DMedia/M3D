"""Port defining the contract for investigation persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

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


class InvestigationStore(ABC):
    """Abstract interface for persisting investigation state and outcomes."""

    @abstractmethod
    def save_investigation(self, investigation: Investigation) -> None:
        """Persist an investigation."""
        raise NotImplementedError

    @abstractmethod
    def get_investigation(self, investigation_id: str) -> Investigation | None:
        """Retrieve an investigation by identifier."""
        raise NotImplementedError

    @abstractmethod
    def save_evidence(self, evidence: Evidence) -> None:
        """Persist investigation evidence."""
        raise NotImplementedError

    @abstractmethod
    def get_evidence(self, investigation_id: str) -> list[Evidence]:
        """Retrieve evidence belonging to an investigation."""
        raise NotImplementedError

    @abstractmethod
    def save_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Persist an investigation hypothesis."""
        raise NotImplementedError

    @abstractmethod
    def get_hypotheses(self, investigation_id: str) -> list[Hypothesis]:
        """Retrieve hypotheses belonging to an investigation."""
        raise NotImplementedError

    @abstractmethod
    def save_decision(self, decision: Decision) -> None:
        """Persist an investigation decision."""
        raise NotImplementedError

    @abstractmethod
    def get_decisions(self, investigation_id: str) -> list[Decision]:
        """Retrieve decisions belonging to an investigation."""
        raise NotImplementedError

    @abstractmethod
    def save_risk(self, risk: Risk) -> None:
        """Persist a decision risk assessment."""
        raise NotImplementedError

    @abstractmethod
    def get_risks(self, decision_id: str) -> list[Risk]:
        """Retrieve risks associated with a decision."""
        raise NotImplementedError

    @abstractmethod
    def save_policy_evaluation(self, evaluation: PolicyEvaluation) -> None:
        """Persist a policy evaluation."""
        raise NotImplementedError

    @abstractmethod
    def get_policy_evaluations(self, decision_id: str) -> list[PolicyEvaluation]:
        """Retrieve policy evaluations for a decision."""
        raise NotImplementedError

    @abstractmethod
    def save_authorization(self, authorization: Authorization) -> None:
        """Persist an authorization record."""
        raise NotImplementedError

    @abstractmethod
    def get_authorization(self, authorization_id: str) -> Authorization | None:
        """Retrieve an authorization by identifier."""
        raise NotImplementedError

    @abstractmethod
    def save_action(self, action: Action) -> None:
        """Persist an operational action."""
        raise NotImplementedError

    @abstractmethod
    def get_action(self, action_id: str) -> Action | None:
        """Retrieve an action by identifier."""
        raise NotImplementedError

    @abstractmethod
    def save_action_result(self, result: ActionResult) -> None:
        """Persist an action execution result."""
        raise NotImplementedError

    @abstractmethod
    def get_action_result(self, action_id: str) -> ActionResult | None:
        """Retrieve the result of an action."""
        raise NotImplementedError

    @abstractmethod
    def save_verification(self, verification: Verification) -> None:
        """Persist an action verification."""
        raise NotImplementedError

    @abstractmethod
    def get_verification(self, action_id: str) -> Verification | None:
        """Retrieve the verification for an action."""
        raise NotImplementedError
