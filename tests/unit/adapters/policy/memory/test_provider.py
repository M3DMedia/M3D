"""Tests for the in-memory policy provider."""

from m3d.adapters.policy.memory import InMemoryPolicyProvider
from m3d.domain.policy import Policy


def test_get_policies_returns_configured_policies() -> None:
    policy = Policy(
        id="policy_test",
        name="Test policy",
        description="Allow a controlled operational action.",
        scope="service",
        conditions=("risk.severity == low",),
        effect="allow",
        status="active",
    )
    provider = InMemoryPolicyProvider([policy])

    assert provider.get_policies() == (policy,)


def test_get_policies_returns_empty_tuple_by_default() -> None:
    provider = InMemoryPolicyProvider()

    assert provider.get_policies() == ()
