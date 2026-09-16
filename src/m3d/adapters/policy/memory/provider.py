"""In-memory policy provider adapter."""

from collections.abc import Sequence

from m3d.domain.policy import Policy
from m3d.ports.policy import PolicyProvider


class InMemoryPolicyProvider(PolicyProvider):
    """Provide policies from an in-memory collection."""

    def __init__(self, policies: Sequence[Policy] = ()) -> None:
        self._policies = tuple(policies)

    def get_policies(self) -> Sequence[Policy]:
        """Return all configured policies."""
        return self._policies
