"""Tests for the policy condition evaluation port."""

from collections.abc import Mapping
from typing import Any

import pytest

from m3d.ports.policy_condition import PolicyConditionEvaluator


class FakeEvaluator(PolicyConditionEvaluator):
    """Minimal evaluator implementation for contract tests."""

    def evaluate(
        self,
        condition: str,
        context: Mapping[str, Any],
    ) -> bool:
        return condition == "test == true"


def test_evaluator_is_abstract() -> None:
    with pytest.raises(TypeError):
        PolicyConditionEvaluator()  # type: ignore[abstract]


def test_evaluator_implementation_can_be_called() -> None:
    evaluator = FakeEvaluator()

    assert (
        evaluator.evaluate(
            "test == true",
            {"test": True},
        )
        is True
    )


def test_evaluator_can_return_false() -> None:
    evaluator = FakeEvaluator()

    assert (
        evaluator.evaluate(
            "test == false",
            {"test": False},
        )
        is False
    )
