"""Domain model for operational environments."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from m3d.domain.common.types import EnvironmentId, utc_now


@dataclass(frozen=True, slots=True)
class Environment:
    """A system or operational boundary managed by M3D."""

    id: EnvironmentId
    name: str
    type: str
    status: str
    metadata: Mapping[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        """Validate the environment's required identity fields."""
        if not self.name.strip():
            raise ValueError("Environment name cannot be empty.")

        if not self.type.strip():
            raise ValueError("Environment type cannot be empty.")

        if not self.status.strip():
            raise ValueError("Environment status cannot be empty.")
