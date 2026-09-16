"""Tests for Linux environment observation."""

from __future__ import annotations

import platform

from m3d.adapters.environments.linux import LinuxEnvironmentPlugin
from m3d.domain.common.types import EnvironmentId


def test_observe_returns_host_observation_event() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")

    events = plugin.observe()

    assert len(events) == 1

    event = events[0]

    assert event.environment_id == EnvironmentId("linux_test")
    assert event.type == "host.observed"
    assert event.severity == "info"
    assert event.source == "linux_environment"
    assert event.entity_id is not None


def test_observe_includes_platform_metadata() -> None:
    plugin = LinuxEnvironmentPlugin()

    event = plugin.observe()[0]

    assert event.metadata["hostname"] == (platform.node() or "unknown-host")
    assert event.metadata["system"] == platform.system()
    assert event.metadata["release"] == platform.release()
    assert event.metadata["machine"] == platform.machine()
    assert event.metadata["processor"] == platform.processor()


def test_observe_generates_event_id() -> None:
    plugin = LinuxEnvironmentPlugin()

    event = plugin.observe()[0]

    assert event.id
    assert str(event.id).startswith("event_")


def test_observe_generates_correlation_id() -> None:
    plugin = LinuxEnvironmentPlugin()

    event = plugin.observe()[0]

    assert event.correlation_id
    assert event.correlation_id.startswith("corr_")


def test_observe_generates_timestamp() -> None:
    plugin = LinuxEnvironmentPlugin()

    event = plugin.observe()[0]

    assert event.timestamp is not None
