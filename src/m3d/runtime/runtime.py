"""M3D runtime orchestration boundary."""

from __future__ import annotations

from m3d.domain.common.types import EnvironmentId
from m3d.domain.entity import Entity
from m3d.domain.event import Event
from m3d.ports.environment import EnvironmentPlugin
from m3d.ports.event_bus import EventBus


class M3DRuntime:
    """Coordinate M3D operations against a configured environment."""

    def __init__(
        self,
        environment: EnvironmentPlugin,
        event_bus: EventBus,
    ) -> None:
        self._environment = environment
        self._event_bus = event_bus

    @property
    def environment(self) -> EnvironmentPlugin:
        """Return the configured environment plugin."""
        return self._environment

    def identify_environment(self) -> EnvironmentId:
        """Return the identifier of the configured environment."""
        return self._environment.identify()

    def discover(self) -> list[Entity]:
        """Discover entities through the configured environment."""
        return self._environment.discover()

    def observe(self) -> list[Event]:
        """Observe the configured environment for events."""
        return self._environment.observe()

    def observe_and_publish(self) -> list[Event]:
        """Observe the environment and publish each resulting event."""
        events = self.observe()

        for event in events:
            self._event_bus.publish(event)

        return events

    def collect(self, target: str) -> dict[str, object]:
        """Collect detailed information through the configured environment."""
        return self._environment.collect(target)

    def execute(
        self,
        operation: str,
        parameters: dict[str, object],
    ) -> dict[str, object]:
        """Execute an explicitly supported operation through the environment."""
        return self._environment.execute(operation, parameters)

    def verify(
        self,
        target: str,
        expected_outcome: str,
    ) -> dict[str, object]:
        """Verify an expected outcome through the configured environment."""
        return self._environment.verify(target, expected_outcome)
