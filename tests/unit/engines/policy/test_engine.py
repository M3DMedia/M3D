"""Tests for the concrete policy evaluation engine."""

from collections.abc import Mapping
from typing import Any

import pytest

from m3d.domain.common.types import DecisionId, InvestigationId, PolicyId
from m3d.domain.decision import Decision
from m3d.domain.policy import Policy
from m3d.engines.policy import DefaultPolicyEngine
from m3d.ports.policy_condition import PolicyConditionEvaluator


class FakeConditionEvaluator(PolicyConditionEvaluator):
    """Deterministic condition evaluator for engine tests."""

    def evaluate(
        self,
        condition: str,
        context: Mapping[str, Any],
    ) -> bool:
        return bool(context.get(condition, False))


def make_decision(
    metadata: dict[str, Any] | None = None,
) -> Decision:
    """Create a valid decision for engine tests."""
    return Decision(
        id=DecisionId("dec_test"),
        investigation_id=InvestigationId("inv_test"),
        decision="restart_service",
        rationale="The service process is unavailable.",
        metadata=metadata or {},
    )


def make_policy(
    *,
    policy_id: str = "pol_test",
    name: str = "Production protection",
    effect: str = "require_approval",
    priority: int = 100,
    conditions: tuple[str, ...] = ("production",),
    status: str = "active",
) -> Policy:
    """Create a valid policy for engine tests."""
    return Policy(
        id=PolicyId(policy_id),
        name=name,
        description="Protect operational environments.",
        scope="production",
        conditions=conditions,
        effect=effect,
        priority=priority,
        status=status,
    )


def test_evaluate_returns_policy_effect() -> None:
    engine = DefaultPolicyEngine(FakeConditionEvaluator())
    decision = make_decision({"production": True})
    policy = make_policy()

    evaluation = engine.evaluate(decision, [policy])

    assert evaluation.decision_id == decision.id
    assert evaluation.policy_id == policy.id
    assert evaluation.result == "approval_required"
    assert evaluation.status == "evaluated"
    assert evaluation.evaluated_at is not None


@pytest.mark.parametrize(
    ("effect", "expected_result"),
    [
        ("allow", "allowed"),
        ("deny", "denied"),
        ("require_approval", "approval_required"),
    ],
)
def test_policy_effect_maps_to_evaluation_result(
    effect: str,
    expected_result: str,
) -> None:
    engine = DefaultPolicyEngine(FakeConditionEvaluator())
    decision = make_decision({"production": True})
    policy = make_policy(effect=effect)

    evaluation = engine.evaluate(decision, [policy])

    assert evaluation.result == expected_result


def test_only_active_policies_are_applicable() -> None:
    engine = DefaultPolicyEngine(FakeConditionEvaluator())
    decision = make_decision({"production": True})

    disabled = make_policy(
        policy_id="pol_disabled",
        priority=1000,
        status="disabled",
    )
    active = make_policy(
        policy_id="pol_active",
        priority=100,
    )

    evaluation = engine.evaluate(decision, [disabled, active])

    assert evaluation.policy_id == active.id


def test_all_policy_conditions_must_pass() -> None:
    engine = DefaultPolicyEngine(FakeConditionEvaluator())
    decision = make_decision(
        {
            "production": True,
            "approved_window": False,
        }
    )
    policy = make_policy(
        conditions=("production", "approved_window"),
    )

    with pytest.raises(ValueError, match="No applicable active policy"):
        engine.evaluate(decision, [policy])


def test_highest_priority_applicable_policy_is_selected() -> None:
    engine = DefaultPolicyEngine(FakeConditionEvaluator())
    decision = make_decision({"production": True})

    lower = make_policy(
        policy_id="pol_low",
        priority=10,
        effect="deny",
    )
    higher = make_policy(
        policy_id="pol_high",
        priority=100,
        effect="require_approval",
    )

    evaluation = engine.evaluate(decision, [lower, higher])

    assert evaluation.policy_id == higher.id
    assert evaluation.result == "approval_required"


def test_non_matching_policy_is_ignored() -> None:
    engine = DefaultPolicyEngine(FakeConditionEvaluator())
    decision = make_decision(
        {
            "production": False,
            "staging": True,
        }
    )

    production = make_policy(
        policy_id="pol_production",
        conditions=("production",),
    )
    staging = make_policy(
        policy_id="pol_staging",
        conditions=("staging",),
    )

    evaluation = engine.evaluate(decision, [production, staging])

    assert evaluation.policy_id == staging.id


def test_no_applicable_policy_raises_value_error() -> None:
    engine = DefaultPolicyEngine(FakeConditionEvaluator())
    decision = make_decision({"production": False})
    policy = make_policy()

    with pytest.raises(ValueError, match="No applicable active policy"):
        engine.evaluate(decision, [policy])
