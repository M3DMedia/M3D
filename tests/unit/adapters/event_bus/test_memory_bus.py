"""Tests for the in-memory event bus adapter."""

from datetime import UTC, datetime

from m3d.adapters.event_bus.memory import InMemoryEventBus
from m3d.domain.common.types import EntityId, EnvironmentId, EventId
from m3d.domain.event import Event


def make_event(event_type: str = "test.created") -> Event:
    """Create a deterministic event for testing."""
    return Event(
        id=EventId("evt_test"),
        timestamp=datetime.now(UTC),
        environment_id=EnvironmentId("env_test"),
        entity_id=EntityId("ent_test"),
        type=event_type,
        severity="info",
        source="test",
    )


def test_publish_delivers_event_to_subscriber() -> None:
    """A subscribed handler receives the published event."""
    bus = InMemoryEventBus()
    received: list[Event] = []

    def handler(event: Event) -> None:
        received.append(event)

    event = make_event()

    bus.subscribe(event.type, handler)
    bus.publish(event)

    assert received == [event]


def test_publish_delivers_event_to_multiple_subscribers() -> None:
    """All subscribed handlers receive the published event."""
    bus = InMemoryEventBus()
    first: list[Event] = []
    second: list[Event] = []

    def first_handler(event: Event) -> None:
        first.append(event)

    def second_handler(event: Event) -> None:
        second.append(event)

    event = make_event()

    bus.subscribe(event.type, first_handler)
    bus.subscribe(event.type, second_handler)
    bus.publish(event)

    assert first == [event]
    assert second == [event]


def test_unsubscribe_stops_event_delivery() -> None:
    """An unsubscribed handler no longer receives published events."""
    bus = InMemoryEventBus()
    received: list[Event] = []

    def handler(event: Event) -> None:
        received.append(event)

    event = make_event()

    bus.subscribe(event.type, handler)
    bus.unsubscribe(event.type, handler)
    bus.publish(event)

    assert received == []
