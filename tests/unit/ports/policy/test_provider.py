"""Tests for the policy provider port."""

from collections.abc import Sequence

from m3d.domain.policy import Policy
from m3d.ports.policy import PolicyProvider


class FakePolicyProvider(PolicyProvider):
    """Minimal policy provider implementation for contract tests."""

    def __init__(self, policies: Sequence[Policy]) -> None:
        self._policies = policies

    def get_policies(self) -> Sequence[Policy]:
        return self._policies


def test_policy_provider_returns_available_policies() -> None:
    policy = Policy(
        id="policy_test",
        name="Test policy",
        description="Allow a controlled operational action.",
        scope="service",
        conditions=("risk.severity == low",),
        effect="allow",
        status="active",
    )
    provider = FakePolicyProvider([policy])

    assert provider.get_policies() == [policy]
