"""Tests for macOS environment observation."""

from __future__ import annotations

import platform

from m3d.adapters.environments.macos import MacOSEnvironmentPlugin
from m3d.domain.common.types import EnvironmentId


def test_observe_returns_host_observation_event() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    events = plugin.observe()

    assert len(events) == 1
    assert events[0].environment_id == EnvironmentId("macos_test")
    assert events[0].type == "host.observed"
    assert events[0].severity == "info"
    assert events[0].source == "macos_environment"


def test_observe_reports_current_hostname() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    event = plugin.observe()[0]

    assert event.metadata["hostname"] == (platform.node() or "unknown-host")


def test_observe_reports_darwin_system() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    event = plugin.observe()[0]

    assert event.metadata["system"] == "Darwin"


def test_observe_links_event_to_discovered_host() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    event = plugin.observe()[0]
    host = plugin.discover()[0]

    assert event.entity_id is not None
    assert event.entity_id != host.id


def test_observe_creates_unique_event_and_correlation_ids() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    first = plugin.observe()[0]
    second = plugin.observe()[0]

    assert first.id != second.id
    assert first.correlation_id != second.correlation_id
