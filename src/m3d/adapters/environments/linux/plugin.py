"""Linux environment adapter."""

from __future__ import annotations

import platform

from m3d.domain.common.types import EntityId, EnvironmentId, EventId, new_id, utc_now
from m3d.domain.entity import Entity
from m3d.domain.event import Event
from m3d.ports.environment import EnvironmentPlugin


class LinuxEnvironmentPlugin(EnvironmentPlugin):
    """Connect M3D to a Linux environment."""

    def __init__(self, environment_id: str = "linux_local") -> None:
        if not environment_id.strip():
            raise ValueError("Environment ID cannot be empty.")

        self._environment_id = EnvironmentId(environment_id)
        self._host_entity_id = EntityId(new_id("entity"))

    def identify(self) -> EnvironmentId:
        """Return the configured Linux environment identifier."""
        return self._environment_id

    def discover(self) -> list[Entity]:
        """Discover the local Linux host."""
        timestamp = utc_now()
        hostname = platform.node() or "unknown-host"

        return [
            Entity(
                id=self._host_entity_id,
                environment_id=self._environment_id,
                type="host",
                name=hostname,
                status="online",
                attributes={
                    "system": platform.system(),
                    "release": platform.release(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                },
                created_at=timestamp,
                updated_at=timestamp,
            )
        ]

    def observe(self) -> list[Event]:
        """Observe the current Linux host and emit a structured event."""
        host = self.discover()[0]

        return [
            Event(
                id=EventId(new_id("event")),
                timestamp=utc_now(),
                environment_id=self._environment_id,
                entity_id=host.id,
                type="host.observed",
                severity="info",
                source="linux_environment",
                metadata={
                    "hostname": host.name,
                    "system": platform.system(),
                    "release": platform.release(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                },
                correlation_id=new_id("corr"),
            )
        ]

    def collect(self, target: str) -> dict[str, object]:
        """Collect detailed information about a Linux target."""
        if not target.strip():
            raise ValueError("Collection target cannot be empty.")

        if target != "host":
            raise ValueError(f"Unsupported collection target: {target}")

        return {
            "target": "host",
            "hostname": platform.node() or "unknown-host",
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }

    def execute(
        self,
        operation: str,
        parameters: dict[str, object],
    ) -> dict[str, object]:
        """Execute an explicitly supported Linux operation."""
        if not operation.strip():
            raise ValueError("Operation cannot be empty.")

        if operation != "get_hostname":
            raise ValueError(f"Unsupported operation: {operation}")

        if parameters:
            raise ValueError("Operation get_hostname does not accept parameters.")

        return {
            "operation": "get_hostname",
            "hostname": platform.node() or "unknown-host",
        }

    def verify(
        self,
        target: str,
        expected_outcome: str,
    ) -> dict[str, object]:
        """Verify an expected outcome in the Linux environment."""
        if not target.strip():
            raise ValueError("Verification target cannot be empty.")

        if not expected_outcome.strip():
            raise ValueError("Expected outcome cannot be empty.")

        if target != "host":
            raise ValueError(f"Unsupported verification target: {target}")

        if expected_outcome == "host_present":
            return {
                "target": "host",
                "expected_outcome": "host_present",
                "verified": True,
                "observed_outcome": "host_present",
                "reason": "Host is present.",
            }

        if expected_outcome == "host_online":
            return {
                "target": "host",
                "expected_outcome": "host_online",
                "verified": True,
                "observed_outcome": "host_online",
                "reason": "Host is online.",
            }

        raise ValueError(f"Unsupported expected outcome: {expected_outcome}")
