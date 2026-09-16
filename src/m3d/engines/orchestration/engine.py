"""Coordinate policy-gated operational actions."""

from __future__ import annotations

from typing import Any

from m3d.domain.action import Action
from m3d.domain.action_result import ActionResult
from m3d.domain.audit import AuditRecord
from m3d.domain.authorization import Authorization
from m3d.domain.common.types import ActionId, AuditRecordId, DecisionId, new_id
from m3d.domain.verification import Verification
from m3d.engines.action import DefaultActionEngine
from m3d.engines.audit import DefaultAuditEngine
from m3d.engines.verification import DefaultVerificationEngine
from m3d.ports.investigation import InvestigationStore


class OperationalOrchestrator:
    """Coordinate the transition from governed decisions to proposed actions."""

    def __init__(
        self,
        store: InvestigationStore,
        action_engine: DefaultActionEngine,
        verification_engine: DefaultVerificationEngine,
        audit_engine: DefaultAuditEngine,
    ) -> None:
        self._store = store
        self._action_engine = action_engine
        self._verification_engine = verification_engine
        self._audit_engine = audit_engine

    def request_authorization(
        self,
        action_id: ActionId,
    ) -> Authorization:
        """Request authorization for a persisted proposed action."""
        action = self._store.get_action(str(action_id))
        if action is None:
            raise ValueError(f"Action not found: {action_id}")

        authorization = self._action_engine.request_authorization(action)
        if authorization.action_id != action.id:
            raise ValueError(
                f"Authorization action ID does not match action: {action.id}"
            )

        self._store.save_authorization(authorization)
        return authorization

    def authorize_action(
        self,
        action_id: ActionId,
        authorization_id: str,
    ) -> Action:
        """Attach a granted authorization to a persisted action."""
        action = self._store.get_action(str(action_id))
        if action is None:
            raise ValueError(f"Action not found: {action_id}")

        authorization = self._store.get_authorization(authorization_id)
        if authorization is None:
            raise ValueError(f"Authorization not found: {authorization_id}")

        if authorization.action_id != action.id:
            raise ValueError(
                f"Authorization action ID does not match action: {action.id}"
            )

        authorized_action = self._action_engine.authorize(action, authorization)
        self._store.save_action(authorized_action)
        return authorized_action

    def execute_action(
        self,
        action_id: ActionId,
    ) -> ActionResult:
        """Execute a persisted authorized action and persist its result."""
        action = self._store.get_action(str(action_id))
        if action is None:
            raise ValueError(f"Action not found: {action_id}")

        result = self._action_engine.execute(action)
        self._store.save_action_result(result)
        return result

    def verify_action(
        self,
        action_id: ActionId,
    ) -> Verification:
        """Verify a persisted action result and persist the verification."""
        action = self._store.get_action(str(action_id))
        if action is None:
            raise ValueError(f"Action not found: {action_id}")

        result = self._store.get_action_result(str(action_id))
        if result is None:
            raise ValueError(f"Action result not found for action: {action_id}")

        verification = self._verification_engine.verify(action, result)
        if verification.action_id != action.id:
            raise ValueError(
                f"Verification action ID does not match action: {action.id}"
            )

        self._store.save_verification(verification)
        return verification

    def propose_action(
        self,
        decision_id: DecisionId,
        action_type: str,
        description: str,
        requested_by: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Action:
        """Create a proposed action only when policy permits it."""
        decision = self._store.get_decision(str(decision_id))
        if decision is None:
            raise ValueError(f"Decision not found: {decision_id}")

        investigation = self._store.get_investigation(str(decision.investigation_id))
        if investigation is None:
            raise ValueError(
                f"Investigation not found: {decision.investigation_id}"
            )

        evaluations = self._store.get_policy_evaluations(str(decision_id))
        if not evaluations:
            raise ValueError(f"No policy evaluation found for decision: {decision_id}")

        evaluation = evaluations[-1]
        if evaluation.decision_id != decision.id:
            raise ValueError(
                f"Policy evaluation decision ID does not match decision: {decision.id}"
            )

        if evaluation.result == "denied":
            raise ValueError(f"Action proposal denied by policy: {evaluation.id}")

        if evaluation.result not in {"allowed", "approval_required"}:
            raise ValueError(
                f"Action proposal requires a valid policy result: {evaluation.result}"
            )

        action_metadata = dict(metadata or {})
        action_metadata["policy_evaluation_id"] = evaluation.id
        action_metadata["policy_result"] = evaluation.result

        action = Action(
            id=ActionId(new_id("action")),
            decision_id=decision.id,
            environment_id=investigation.environment_id,
            action_type=action_type,
            description=description,
            requested_by=requested_by,
            metadata=action_metadata,
        )
        self._store.save_action(action)

        correlation_id = str(action_metadata.get("correlation_id") or action.id)

        self._audit_engine.record(
            AuditRecord(
                id=AuditRecordId(new_id("audit")),
                event_type="action.proposed",
                actor=requested_by or "system",
                description=action.description,
                correlation_id=correlation_id,
                metadata={
                    "investigation_id": str(investigation.id),
                    "decision_id": str(decision.id),
                    "action_id": str(action.id),
                    "policy_evaluation_id": str(evaluation.id),
                    "policy_result": evaluation.result,
                },
            )
        )

        return action
