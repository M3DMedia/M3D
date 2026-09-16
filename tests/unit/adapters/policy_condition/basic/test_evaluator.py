"""Tests for the basic policy condition evaluator."""

import pytest

from m3d.adapters.policy_condition.basic import BasicPolicyConditionEvaluator


def test_equality_condition() -> None:
    evaluator = BasicPolicyConditionEvaluator()

    assert (
        evaluator.evaluate(
            "environment == production",
            {"environment": "production"},
        )
        is True
    )


def test_equality_condition_returns_false_when_not_matching() -> None:
    evaluator = BasicPolicyConditionEvaluator()

    assert (
        evaluator.evaluate(
            "environment == production",
            {"environment": "staging"},
        )
        is False
    )


def test_nested_field_condition() -> None:
    evaluator = BasicPolicyConditionEvaluator()

    assert (
        evaluator.evaluate(
            "risk.severity == high",
            {"risk": {"severity": "high"}},
        )
        is True
    )


@pytest.mark.parametrize(
    ("condition", "context", "expected"),
    [
        ("value != 10", {"value": 5}, True),
        ("value >= 10", {"value": 10}, True),
        ("value <= 10", {"value": 5}, True),
        ("value > 10", {"value": 11}, True),
        ("value < 10", {"value": 9}, True),
    ],
)
def test_comparison_operators(
    condition: str,
    context: dict[str, object],
    expected: bool,
) -> None:
    evaluator = BasicPolicyConditionEvaluator()

    assert evaluator.evaluate(condition, context) is expected


def test_numeric_values_are_parsed() -> None:
    evaluator = BasicPolicyConditionEvaluator()

    assert (
        evaluator.evaluate(
            "risk.score >= 0.8",
            {"risk": {"score": 0.9}},
        )
        is True
    )


def test_boolean_values_are_parsed() -> None:
    evaluator = BasicPolicyConditionEvaluator()

    assert (
        evaluator.evaluate(
            "maintenance == true",
            {"maintenance": True},
        )
        is True
    )


def test_quoted_string_values_are_parsed() -> None:
    evaluator = BasicPolicyConditionEvaluator()

    assert (
        evaluator.evaluate(
            'environment == "production"',
            {"environment": "production"},
        )
        is True
    )


def test_empty_condition_is_rejected() -> None:
    evaluator = BasicPolicyConditionEvaluator()

    with pytest.raises(ValueError, match="condition cannot be empty"):
        evaluator.evaluate(" ", {})


def test_unsupported_operator_is_rejected() -> None:
    evaluator = BasicPolicyConditionEvaluator()

    with pytest.raises(ValueError, match="Unsupported policy condition"):
        evaluator.evaluate("environment in production", {"environment": "production"})


def test_missing_context_field_is_rejected() -> None:
    evaluator = BasicPolicyConditionEvaluator()

    with pytest.raises(KeyError, match="Policy context field not found"):
        evaluator.evaluate(
            "risk.severity == high",
            {"risk": {}},
        )
