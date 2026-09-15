"""Port defining the contract for event publication and subscription."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from m3d.domain.event import Event

EventHandler = Callable[[Event], None]


class EventBus(ABC):
    """Abstract interface for publishing and subscribing to domain events."""

    @abstractmethod
    def publish(self, event: Event) -> None:
        """Publish an event to all matching subscribers."""
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to events of a specific type."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Remove a previously registered event handler."""
        raise NotImplementedError
