"""Tests for the Linux environment adapter."""

from __future__ import annotations

import pytest

from m3d.adapters.environments.linux import LinuxEnvironmentPlugin
from m3d.domain.common.types import EnvironmentId


def test_identify_returns_configured_environment_id() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")

    assert plugin.identify() == EnvironmentId("linux_test")


def test_identify_uses_default_environment_id() -> None:
    plugin = LinuxEnvironmentPlugin()

    assert plugin.identify() == EnvironmentId("linux_local")


def test_empty_environment_id_is_rejected() -> None:
    with pytest.raises(ValueError, match="Environment ID cannot be empty"):
        LinuxEnvironmentPlugin(" ")


def test_environment_id_is_stable() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")

    assert plugin.identify() == plugin.identify()

def test_observe_references_the_discovered_host_entity() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")

    discovered = plugin.discover()[0]
    observed = plugin.observe()[0]

    assert observed.entity_id == discovered.id
    assert observed.environment_id == plugin.identify()
