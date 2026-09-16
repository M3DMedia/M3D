"""Tests for the action result domain model."""

from __future__ import annotations

import pytest

from m3d.domain.action_result.action_result import (
    ACTION_RESULT_STATUSES,
    ActionResult,
)
from m3d.domain.common.types import ActionId, EntityId


def make_result(status: str = "succeeded") -> ActionResult:
    """Create a test action result."""
    return ActionResult(
        id="act_result_test",
        action_id=ActionId("act_test"),
        status=status,
    )


@pytest.mark.parametrize("status", ACTION_RESULT_STATUSES)
def test_all_valid_statuses_are_accepted(status: str) -> None:
    """Every defined action result status is accepted."""
    if status == "failed":
        result = ActionResult(
            id="act_result_test",
            action_id=ActionId("act_test"),
            status=status,
            error="Service restart failed.",
        )
    else:
        result = make_result(status)

    assert result.status == status


def test_unknown_status_is_rejected() -> None:
    """Unknown action result statuses are rejected."""
    with pytest.raises(ValueError, match="Invalid action result status"):
        make_result("unknown")


def test_empty_id_is_rejected() -> None:
    """An action result requires an identifier."""
    with pytest.raises(ValueError, match="ID cannot be empty"):
        ActionResult(
            id="",
            action_id=ActionId("act_test"),
            status="succeeded",
        )


def test_failed_result_requires_error() -> None:
    """A failed action result must contain an error."""
    with pytest.raises(ValueError, match="must contain an error"):
        make_result("failed")


def test_failed_result_accepts_error() -> None:
    """A failed action result may contain its error."""
    result = ActionResult(
        id="act_result_test",
        action_id=ActionId("act_test"),
        status="failed",
        error="Service restart failed.",
    )

    assert result.error == "Service restart failed."


def test_output_can_be_recorded() -> None:
    """Execution output can be recorded."""
    result = ActionResult(
        id="act_result_test",
        action_id=ActionId("act_test"),
        status="succeeded",
        output="Service restarted successfully.",
    )

    assert result.output == "Service restarted successfully."


def test_affected_entities_can_be_recorded() -> None:
    """Affected entities can be recorded."""
    result = ActionResult(
        id="act_result_test",
        action_id=ActionId("act_test"),
        status="succeeded",
        affected_entities=(
            EntityId("ent_service"),
            EntityId("ent_host"),
        ),
    )

    assert result.affected_entities == (
        EntityId("ent_service"),
        EntityId("ent_host"),
    )


def test_action_id_is_preserved() -> None:
    """The result identifies the action that produced it."""
    result = make_result()

    assert result.action_id == ActionId("act_test")


def test_result_is_immutable() -> None:
    """Action result instances cannot be mutated."""
    result = make_result()

    with pytest.raises(AttributeError):
        result.status = "failed"  # type: ignore[misc]
