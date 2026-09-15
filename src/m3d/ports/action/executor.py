"""Port defining the contract for operational action execution."""

from __future__ import annotations

from abc import ABC, abstractmethod

from m3d.domain.action import Action
from m3d.domain.action_result import ActionResult


class ActionExecutor(ABC):
    """Abstract interface for executing authorized operational actions."""

    @abstractmethod
    def execute(self, action: Action) -> ActionResult:
        """Execute an authorized action and return its actual result."""
        raise NotImplementedError
