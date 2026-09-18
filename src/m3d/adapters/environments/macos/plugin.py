"""macOS environment adapter."""

from __future__ import annotations

import hashlib
import platform
import re
import shutil
import subprocess
import time

from m3d.domain.common.types import EntityId, EnvironmentId, EventId, new_id, utc_now
from m3d.domain.entity import Entity
from m3d.domain.event import Event
from m3d.ports.environment import EnvironmentPlugin


class MacOSEnvironmentPlugin(EnvironmentPlugin):
    """Connect M3D to a macOS environment."""

    def __init__(self, environment_id: str = "macos_local") -> None:
        if not environment_id.strip():
            raise ValueError("Environment ID cannot be empty.")

        self._environment_id = EnvironmentId(environment_id)
        self._host_entity_id = EntityId(self._build_host_entity_id())

    def _run_command(self, command: list[str]) -> str:
        """Run a read-only macOS command and return its stdout."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
        except (OSError, subprocess.SubprocessError):
            return ""

        return result.stdout.strip()

    def _build_host_entity_id(self) -> str:
        """Build a deterministic opaque host entity ID for this macOS host."""
        hardware_output = self._run_command(
            ["system_profiler", "SPHardwareDataType"]
        )

        hardware_uuid = next(
            (
                line.split(":", 1)[1].strip()
                for line in hardware_output.splitlines()
                if line.strip().startswith("Hardware UUID:")
            ),
            "",
        )

        identity_source = hardware_uuid or platform.node() or "unknown-host"
        digest = hashlib.sha256(
            f"{self._environment_id}:{identity_source}".encode()
        ).hexdigest()
        return f"entity_{digest[:32]}"

    def _hardware_information(self) -> dict[str, object]:
        """Collect hardware information from macOS."""
        output = self._run_command(
            ["system_profiler", "SPHardwareDataType"]
        )

        information: dict[str, object] = {}

        field_mapping = {
            "Model Name:": "model_name",
            "Model Identifier:": "model_identifier",
            "Chip:": "chip",
            "Total Number of Cores:": "core_count",
            "Memory:": "memory",
        }

        for line in output.splitlines():
            stripped = line.strip()

            for source_field, target_field in field_mapping.items():
                if stripped.startswith(source_field):
                    information[target_field] = stripped.split(":", 1)[1].strip()
                    break

        return information

    def _software_information(self) -> dict[str, object]:
        """Collect macOS version information."""
        output = self._run_command(["sw_vers"])

        information: dict[str, object] = {}

        field_mapping = {
            "ProductName:": "product_name",
            "ProductVersion:": "product_version",
            "BuildVersion:": "build_version",
        }

        for line in output.splitlines():
            stripped = line.strip()

            for source_field, target_field in field_mapping.items():
                if stripped.startswith(source_field):
                    information[target_field] = stripped.split(":", 1)[1].strip()
                    break

        return information

    def _cpu_count(self) -> int | None:
        """Return the logical CPU count reported by macOS."""
        output = self._run_command(["sysctl", "-n", "hw.ncpu"])

        try:
            return int(output)
        except ValueError:
            return None

    def _memory_total(self) -> int | None:
        """Return total physical memory in bytes."""
        output = self._run_command(["sysctl", "-n", "hw.memsize"])

        try:
            return int(output)
        except ValueError:
            return None

    def _uptime_seconds(self) -> float | None:
        """Return the host uptime in seconds."""
        output = self._run_command(["sysctl", "-n", "kern.boottime"])

        match = re.search(r"sec\s*=\s*(\d+)", output)
        if not match:
            return None

        boot_timestamp = int(match.group(1))
        return max(0.0, time.time() - boot_timestamp)

    def _storage_information(self) -> dict[str, object]:
        """Collect storage information for the root filesystem."""
        total, used, free = shutil.disk_usage("/")

        usage_percent = (used / total * 100) if total else 0.0

        return {
            "mount_point": "/",
            "total_bytes": total,
            "used_bytes": used,
            "free_bytes": free,
            "usage_percent": round(usage_percent, 2),
        }

    def identify(self) -> EnvironmentId:
        """Return the configured macOS environment identifier."""
        return self._environment_id

    def discover(self) -> list[Entity]:
        """Discover the local macOS host."""
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
        """Observe the current macOS host and emit a structured event."""
        host = self.discover()[0]

        return [
            Event(
                id=EventId(new_id("event")),
                timestamp=utc_now(),
                environment_id=self._environment_id,
                entity_id=host.id,
                type="host.observed",
                severity="info",
                source="macos_environment",
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
        """Collect detailed information about a macOS target."""
        if not target.strip():
            raise ValueError("Collection target cannot be empty.")

        if target != "host":
            raise ValueError(f"Unsupported collection target: {target}")

        hardware = self._hardware_information()
        software = self._software_information()

        return {
            "target": "host",
            "hostname": platform.node() or "unknown-host",
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.machine(),
            "cpu_count": self._cpu_count(),
            "memory_total_bytes": self._memory_total(),
            "uptime_seconds": self._uptime_seconds(),
            "hardware": hardware,
            "software": software,
            "storage": self._storage_information(),
        }

    def execute(
        self,
        operation: str,
        parameters: dict[str, object],
    ) -> dict[str, object]:
        """Execute an explicitly supported macOS operation."""
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
        """Verify an expected outcome in the macOS environment."""
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
