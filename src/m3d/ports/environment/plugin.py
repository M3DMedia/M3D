"""Port defining the contract for operational environment plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from m3d.domain.common.types import EnvironmentId
from m3d.domain.entity import Entity
from m3d.domain.event import Event


class EnvironmentPlugin(ABC):
    """Abstract interface for connecting M3D to an operational environment."""

    @abstractmethod
    def identify(self) -> EnvironmentId:
        """Return the identifier of the environment handled by this plugin."""
        raise NotImplementedError

    @abstractmethod
    def discover(self) -> list[Entity]:
        """Discover entities currently present in the environment."""
        raise NotImplementedError

    @abstractmethod
    def observe(self) -> list[Event]:
        """Observe the environment and return newly detected events."""
        raise NotImplementedError

    @abstractmethod
    def collect(self, target: str) -> dict[str, Any]:
        """Collect detailed information about a target in the environment."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, operation: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute an explicitly requested operation in the environment."""
        raise NotImplementedError

    @abstractmethod
    def verify(self, target: str, expected_outcome: str) -> dict[str, Any]:
        """Verify whether an expected operational outcome occurred."""
        raise NotImplementedError
