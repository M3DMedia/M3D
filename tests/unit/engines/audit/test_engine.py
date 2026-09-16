"""Tests for the audit orchestration engine."""

from __future__ import annotations

from datetime import UTC, datetime

from m3d.adapters.storage.memory import InMemoryAuditStore
from m3d.domain.audit import AuditRecord
from m3d.domain.common.types import AuditRecordId
from m3d.engines.audit import DefaultAuditEngine


def make_record(
    record_id: str,
    correlation_id: str = "corr_001",
) -> AuditRecord:
    return AuditRecord(
        id=AuditRecordId(record_id),
        event_type="action.created",
        actor="system",
        description="Action created.",
        correlation_id=correlation_id,
        timestamp=datetime.now(UTC),
    )


def test_record_persists_and_returns_audit_record() -> None:
    store = InMemoryAuditStore()
    engine = DefaultAuditEngine(store)
    record = make_record("audit_001")

    result = engine.record(record)

    assert result == record
    assert store.get("audit_001") == record


def test_get_returns_persisted_record() -> None:
    store = InMemoryAuditStore()
    engine = DefaultAuditEngine(store)
    record = make_record("audit_001")

    store.append(record)

    assert engine.get("audit_001") == record


def test_get_returns_none_for_missing_record() -> None:
    store = InMemoryAuditStore()
    engine = DefaultAuditEngine(store)

    assert engine.get("audit_missing") is None


def test_list_by_correlation_delegates_to_store() -> None:
    store = InMemoryAuditStore()
    engine = DefaultAuditEngine(store)

    first = make_record("audit_001", "corr_001")
    second = make_record("audit_002", "corr_001")
    unrelated = make_record("audit_003", "corr_002")

    store.append(first)
    store.append(second)
    store.append(unrelated)

    assert engine.list_by_correlation("corr_001") == [first, second]
