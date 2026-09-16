"""Tests for the immutable audit record domain model and lifecycle."""

from __future__ import annotations

import pytest

from m3d.domain.audit.audit import AUDIT_STATES, AuditRecord
from m3d.domain.common.types import AuditRecordId


def make_record(state: str = "created") -> AuditRecord:
    """Create a test audit record."""
    return AuditRecord(
        id=AuditRecordId("aud_test"),
        event_type="action.completed",
        actor="system",
        description="The operational action completed successfully.",
        state=state,
        correlation_id="corr_test",
    )


def test_created_can_be_sealed() -> None:
    """Created audit records can be sealed."""
    record = make_record()

    sealed = record.transition_to("sealed")

    assert sealed.state == "sealed"


def test_sealed_is_terminal() -> None:
    """Sealed audit records cannot transition further."""
    record = make_record("sealed")

    with pytest.raises(ValueError, match="Invalid audit transition"):
        record.transition_to("created")


@pytest.mark.parametrize(
    "target",
    [
        "created",
        "sealed",
    ],
)
def test_created_rejects_invalid_or_redundant_transition(target: str) -> None:
    """Created records reject every transition except sealing."""
    if target == "sealed":
        pytest.skip("Sealing is the only valid transition.")

    record = make_record()

    with pytest.raises(ValueError, match="Invalid audit transition"):
        record.transition_to(target)


@pytest.mark.parametrize("state", AUDIT_STATES)
def test_all_valid_states_are_accepted(state: str) -> None:
    """Every defined audit state is accepted."""
    record = make_record(state)

    assert record.state == state


def test_unknown_state_is_rejected() -> None:
    """Unknown audit states are rejected."""
    with pytest.raises(ValueError, match="Invalid audit state"):
        make_record("unknown")


def test_empty_id_is_rejected() -> None:
    """An audit record requires an identifier."""
    with pytest.raises(ValueError, match="ID cannot be empty"):
        AuditRecord(
            id=AuditRecordId(""),
            event_type="action.completed",
            actor="system",
            description="The operational action completed successfully.",
        )


def test_empty_event_type_is_rejected() -> None:
    """An audit record requires an event type."""
    with pytest.raises(ValueError, match="event type cannot be empty"):
        AuditRecord(
            id=AuditRecordId("aud_test"),
            event_type="",
            actor="system",
            description="The operational action completed successfully.",
        )


def test_empty_actor_is_rejected() -> None:
    """An audit record requires an actor."""
    with pytest.raises(ValueError, match="actor cannot be empty"):
        AuditRecord(
            id=AuditRecordId("aud_test"),
            event_type="action.completed",
            actor="",
            description="The operational action completed successfully.",
        )


def test_empty_description_is_rejected() -> None:
    """An audit record requires a description."""
    with pytest.raises(ValueError, match="description cannot be empty"):
        AuditRecord(
            id=AuditRecordId("aud_test"),
            event_type="action.completed",
            actor="system",
            description="",
        )


def test_transition_returns_new_instance() -> None:
    """Audit transitions preserve immutability."""
    record = make_record()

    sealed = record.transition_to("sealed")

    assert sealed is not record
    assert record.state == "created"
    assert sealed.state == "sealed"


def test_transition_preserves_identity_and_provenance() -> None:
    """Sealing preserves the record's identity and provenance fields."""
    record = make_record()

    sealed = record.transition_to("sealed")

    assert sealed.id == record.id
    assert sealed.event_type == record.event_type
    assert sealed.actor == record.actor
    assert sealed.description == record.description
    assert sealed.correlation_id == record.correlation_id
    assert sealed.timestamp == record.timestamp


def test_audit_record_is_immutable() -> None:
    """Audit records cannot be mutated."""
    record = make_record()

    with pytest.raises(AttributeError):
        record.state = "sealed"  # type: ignore[misc]
