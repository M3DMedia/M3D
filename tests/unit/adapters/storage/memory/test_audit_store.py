"""Tests for the in-memory audit store."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from m3d.adapters.storage.memory.audit_store import InMemoryAuditStore
from m3d.domain.audit import AuditRecord
from m3d.domain.common.types import AuditRecordId


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


def test_append_and_get_record() -> None:
    store = InMemoryAuditStore()
    record = make_record("audit_001")

    store.append(record)

    assert store.get("audit_001") == record


def test_get_missing_record_returns_none() -> None:
    store = InMemoryAuditStore()

    assert store.get("audit_missing") is None


def test_append_rejects_duplicate_record_id() -> None:
    store = InMemoryAuditStore()
    record = make_record("audit_001")

    store.append(record)

    with pytest.raises(ValueError, match="Audit record already exists"):
        store.append(record)


def test_list_by_correlation_returns_matching_records_in_append_order() -> None:
    store = InMemoryAuditStore()

    first = make_record("audit_001", "corr_001")
    unrelated = make_record("audit_002", "corr_002")
    second = make_record("audit_003", "corr_001")

    store.append(first)
    store.append(unrelated)
    store.append(second)

    assert store.list_by_correlation("corr_001") == [first, second]


def test_list_by_correlation_returns_empty_list_when_not_found() -> None:
    store = InMemoryAuditStore()

    assert store.list_by_correlation("corr_missing") == []
