"""Port defining the contract for immutable audit persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from m3d.domain.audit import AuditRecord


class AuditStore(ABC):
    """Abstract interface for append-only audit history."""

    @abstractmethod
    def append(self, record: AuditRecord) -> None:
        """Append an audit record to the immutable audit history."""
        raise NotImplementedError

    @abstractmethod
    def get(self, record_id: str) -> AuditRecord | None:
        """Retrieve an audit record by identifier."""
        raise NotImplementedError

    @abstractmethod
    def list_by_correlation(self, correlation_id: str) -> list[AuditRecord]:
        """Retrieve audit records belonging to a correlation chain."""
        raise NotImplementedError
