"""Basic deterministic policy condition evaluator."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from m3d.ports.policy_condition import PolicyConditionEvaluator


class BasicPolicyConditionEvaluator(PolicyConditionEvaluator):
    """Evaluate simple comparison conditions against a runtime context."""

    OPERATORS = ("==", "!=", ">=", "<=", ">", "<")

    def evaluate(
        self,
        condition: str,
        context: Mapping[str, Any],
    ) -> bool:
        """Evaluate a single comparison condition."""
        if not condition.strip():
            raise ValueError("Policy condition cannot be empty.")

        operator = next(
            (candidate for candidate in self.OPERATORS if candidate in condition),
            None,
        )
        if operator is None:
            raise ValueError(f"Unsupported policy condition: {condition}")

        left, right = condition.split(operator, 1)
        field = left.strip()
        expected = right.strip()

        if not field:
            raise ValueError("Policy condition field cannot be empty.")

        if not expected:
            raise ValueError("Policy condition value cannot be empty.")

        actual = self._resolve(field, context)
        expected_value = self._parse_value(expected)

        return self._compare(actual, operator, expected_value)

    def _resolve(self, field: str, context: Mapping[str, Any]) -> Any:
        """Resolve a dotted field path from the context."""
        current: Any = context

        for part in field.split("."):
            if not isinstance(current, Mapping) or part not in current:
                raise KeyError(f"Policy context field not found: {field}")
            current = current[part]

        return current

    def _parse_value(self, value: str) -> Any:
        """Parse a basic scalar policy value."""
        if value.lower() == "true":
            return True

        if value.lower() == "false":
            return False

        if value.lower() == "none":
            return None

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            return value[1:-1]

        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            return value

    def _compare(
        self,
        actual: Any,
        operator: str,
        expected: Any,
    ) -> bool:
        """Apply a supported comparison operator."""
        if operator == "==":
            return bool(actual == expected)

        if operator == "!=":
            return bool(actual != expected)

        if operator == ">=":
            return bool(actual >= expected)

        if operator == "<=":
            return bool(actual <= expected)

        if operator == ">":
            return bool(actual > expected)

        if operator == "<":
            return bool(actual < expected)

        raise ValueError(f"Unsupported policy operator: {operator}")
