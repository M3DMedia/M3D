"""Concrete policy evaluation engine."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import ClassVar

from m3d.domain.common.types import PolicyId, new_id
from m3d.domain.decision import Decision
from m3d.domain.policy import Policy
from m3d.domain.policy_evaluation import PolicyEvaluation
from m3d.ports.policy import PolicyEngine
from m3d.ports.policy_condition import PolicyConditionEvaluator


class DefaultPolicyEngine(PolicyEngine):
    """Evaluate active policies against a decision context."""

    EFFECT_RESULTS: ClassVar[dict[str, str]] = {
        "allow": "allowed",
        "deny": "denied",
        "require_approval": "approval_required",
    }

    def __init__(self, condition_evaluator: PolicyConditionEvaluator) -> None:
        self._condition_evaluator = condition_evaluator

    def evaluate(
        self,
        decision: Decision,
        policies: Sequence[Policy],
    ) -> PolicyEvaluation:
        """Evaluate policies and return the highest-priority applicable result."""
        applicable: list[Policy] = []

        for policy in policies:
            if policy.status != "active":
                continue

            if all(
                self._condition_evaluator.evaluate(
                    condition,
                    decision.metadata,
                )
                for condition in policy.conditions
            ):
                applicable.append(policy)

        if not applicable:
            raise ValueError(f"No applicable active policy found for decision: {decision.id}")

        selected = max(applicable, key=lambda policy: policy.priority)
        result = self.EFFECT_RESULTS[selected.effect]

        return PolicyEvaluation(
            id=new_id("policy_eval"),
            decision_id=decision.id,
            policy_id=PolicyId(selected.id),
            result=result,
            reason=f"Policy '{selected.name}' evaluated with effect '{selected.effect}'.",
            status="evaluated",
            evaluated_at=datetime.now(UTC),
            metadata={
                "policy_priority": selected.priority,
                "policy_scope": selected.scope,
            },
        )
