"""Tests for the M3D runtime."""

from __future__ import annotations

from m3d.adapters.environments.linux import LinuxEnvironmentPlugin
from m3d.domain.common.types import EnvironmentId
from m3d.runtime import M3DRuntime


def test_runtime_accepts_environment_plugin() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")

    runtime = M3DRuntime(plugin)

    assert runtime.environment is plugin


def test_runtime_identifies_environment() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")
    runtime = M3DRuntime(plugin)

    assert runtime.identify_environment() == EnvironmentId("linux_test")


def test_runtime_discovers_environment() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")
    runtime = M3DRuntime(plugin)

    entities = runtime.discover()

    assert len(entities) == 1
    assert entities[0].environment_id == EnvironmentId("linux_test")
    assert entities[0].type == "host"


def test_runtime_observes_environment() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")
    runtime = M3DRuntime(plugin)

    events = runtime.observe()

    assert len(events) == 1
    assert events[0].environment_id == EnvironmentId("linux_test")
    assert events[0].type == "host.observed"


def test_runtime_collects_environment_data() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")
    runtime = M3DRuntime(plugin)

    data = runtime.collect("host")

    assert data["target"] == "host"
    assert data["hostname"]
    assert data["system"]


def test_runtime_executes_environment_operation() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")
    runtime = M3DRuntime(plugin)

    result = runtime.execute("get_hostname", {})

    assert result["operation"] == "get_hostname"
    assert result["hostname"]


def test_runtime_verifies_environment_outcome() -> None:
    plugin = LinuxEnvironmentPlugin("linux_test")
    runtime = M3DRuntime(plugin)

    result = runtime.verify("host", "host_present")

    assert result["target"] == "host"
    assert result["expected_outcome"] == "host_present"
    assert result["verified"] is True
