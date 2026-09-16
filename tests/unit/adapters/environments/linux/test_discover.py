"""Tests for Linux environment discovery."""

from __future__ import annotations

import platform

from m3d.adapters.environments.linux import LinuxEnvironmentPlugin
from m3d.domain.common.types import EnvironmentId


def test_discover_returns_local_host() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")

    entities = plugin.discover()

    assert len(entities) == 1

    host = entities[0]

    assert host.environment_id == EnvironmentId("linux_test")
    assert host.type == "host"
    assert host.name == (platform.node() or "unknown-host")
    assert host.status == "online"


def test_discover_includes_platform_attributes() -> None:
    plugin = LinuxEnvironmentPlugin()

    host = plugin.discover()[0]

    assert host.attributes["system"] == platform.system()
    assert host.attributes["release"] == platform.release()
    assert host.attributes["machine"] == platform.machine()
    assert host.attributes["processor"] == platform.processor()


def test_discover_generates_entity_id() -> None:
    plugin = LinuxEnvironmentPlugin()

    host = plugin.discover()[0]

    assert host.id
    assert str(host.id).startswith("entity_")


def test_discover_uses_current_timestamps() -> None:
    plugin = LinuxEnvironmentPlugin()

    host = plugin.discover()[0]

    assert host.created_at == host.updated_at
