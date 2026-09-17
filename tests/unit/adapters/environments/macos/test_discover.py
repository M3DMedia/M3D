"""Tests for macOS environment discovery."""

from __future__ import annotations

import platform

import pytest

from m3d.adapters.environments.macos import MacOSEnvironmentPlugin
from m3d.domain.common.types import EnvironmentId

pytestmark = pytest.mark.macos

def test_discover_returns_local_mac_host() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    entities = plugin.discover()

    assert len(entities) == 1
    assert entities[0].environment_id == EnvironmentId("macos_test")
    assert entities[0].type == "host"
    assert entities[0].name == (platform.node() or "unknown-host")
    assert entities[0].status == "online"


def test_discover_reports_macos_system() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    entities = plugin.discover()

    assert entities[0].attributes["system"] == "Darwin"


def test_discover_reports_host_machine() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    entities = plugin.discover()

    assert entities[0].attributes["machine"] == platform.machine()


def test_discover_returns_stable_entity_ids() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    first = plugin.discover()[0]
    second = plugin.discover()[0]

    assert first.id == second.id


def test_discover_returns_stable_entity_ids_across_instances() -> None:
    first_plugin = MacOSEnvironmentPlugin("macos_test")
    second_plugin = MacOSEnvironmentPlugin("macos_test")

    first = first_plugin.discover()[0]
    second = second_plugin.discover()[0]

    assert first.id == second.id
