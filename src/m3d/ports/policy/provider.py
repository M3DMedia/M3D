"""Port defining the contract for retrieving operational policies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from m3d.domain.policy import Policy


class PolicyProvider(ABC):
    """Abstract interface for retrieving policies available for evaluation."""

    @abstractmethod
    def get_policies(self) -> Sequence[Policy]:
        """Return policies available for operational evaluation."""
        raise NotImplementedError
