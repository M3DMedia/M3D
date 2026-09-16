"""In-memory implementation of the immutable audit persistence port."""

from __future__ import annotations

from m3d.domain.audit import AuditRecord
from m3d.ports.audit import AuditStore


class InMemoryAuditStore(AuditStore):
    """Store immutable audit history in memory."""

    def __init__(self) -> None:
        self._records: dict[str, AuditRecord] = {}

    def append(self, record: AuditRecord) -> None:
        """Append a record without allowing an existing ID to be replaced."""
        if record.id in self._records:
            raise ValueError(f"Audit record already exists: {record.id}")

        self._records[record.id] = record

    def get(self, record_id: str) -> AuditRecord | None:
        """Retrieve an audit record by identifier."""
        return self._records.get(record_id)

    def list_by_correlation(self, correlation_id: str) -> list[AuditRecord]:
        """Return audit records for a correlation chain in append order."""
        return [
            record for record in self._records.values() if record.correlation_id == correlation_id
        ]
