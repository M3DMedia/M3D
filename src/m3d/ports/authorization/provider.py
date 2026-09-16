"""Port defining the contract for operational authorization."""

from __future__ import annotations

from abc import ABC, abstractmethod

from m3d.domain.action import Action
from m3d.domain.authorization import Authorization


class AuthorizationProvider(ABC):
    """Abstract interface for requesting authorization for an action."""

    @abstractmethod
    def request(self, action: Action) -> Authorization:
        """Create an authorization request for an operational action."""
        raise NotImplementedError
