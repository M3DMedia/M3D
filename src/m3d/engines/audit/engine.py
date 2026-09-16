"""Audit orchestration engine."""

from __future__ import annotations

from m3d.domain.audit import AuditRecord
from m3d.ports.audit import AuditStore


class DefaultAuditEngine:
    """Orchestrate immutable audit record persistence."""

    def __init__(self, store: AuditStore) -> None:
        self._store = store

    def record(self, record: AuditRecord) -> AuditRecord:
        """Append an audit record and return the persisted record."""
        self._store.append(record)

        persisted = self._store.get(record.id)
        if persisted is None:
            raise RuntimeError(f"Audit record was not persisted: {record.id}")

        return persisted

    def get(self, record_id: str) -> AuditRecord | None:
        """Retrieve an audit record by identifier."""
        return self._store.get(record_id)

    def list_by_correlation(self, correlation_id: str) -> list[AuditRecord]:
        """Retrieve audit records belonging to a correlation chain."""
        return self._store.list_by_correlation(correlation_id)
