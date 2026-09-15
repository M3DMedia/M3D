"""Port defining the contract for operational state persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from m3d.domain.audit import AuditRecord
from m3d.domain.entity import Entity
from m3d.domain.event import Event
from m3d.domain.investigation import Investigation
from m3d.domain.relationship import Relationship


class StateStore(ABC):
    """Abstract interface for persisting and retrieving operational state."""

    @abstractmethod
    def save_entity(self, entity: Entity) -> None:
        """Persist an operational entity."""
        raise NotImplementedError

    @abstractmethod
    def get_entity(self, entity_id: str) -> Entity | None:
        """Retrieve an operational entity by identifier."""
        raise NotImplementedError

    @abstractmethod
    def save_relationship(self, relationship: Relationship) -> None:
        """Persist a relationship between operational entities."""
        raise NotImplementedError

    @abstractmethod
    def save_event(self, event: Event) -> None:
        """Persist an immutable operational event."""
        raise NotImplementedError

    @abstractmethod
    def get_events(self, entity_id: str | None = None) -> list[Event]:
        """Retrieve persisted events, optionally filtered by entity."""
        raise NotImplementedError

    @abstractmethod
    def save_investigation(self, investigation: Investigation) -> None:
        """Persist an operational investigation."""
        raise NotImplementedError

    @abstractmethod
    def get_investigation(self, investigation_id: str) -> Investigation | None:
        """Retrieve an investigation by identifier."""
        raise NotImplementedError

    @abstractmethod
    def save_audit_record(self, record: AuditRecord) -> None:
        """Append an audit record to the operational history."""
        raise NotImplementedError
