"""In-memory implementation of the event bus port."""

from __future__ import annotations

from collections import defaultdict

from m3d.domain.event import Event
from m3d.ports.event_bus import EventBus, EventHandler


class InMemoryEventBus(EventBus):
    """Simple synchronous event bus for local runtime execution."""

    def __init__(self) -> None:
        """Initialize the event subscriber registry."""
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def publish(self, event: Event) -> None:
        """Publish an event to all handlers subscribed to its type."""
        for handler in tuple(self._subscribers.get(event.type, ())):
            handler(event)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for a specific event type."""
        if not event_type.strip():
            raise ValueError("Event type cannot be empty.")

        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Remove a handler from a specific event type."""
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
            except ValueError:
                return

            if not self._subscribers[event_type]:
                del self._subscribers[event_type]
