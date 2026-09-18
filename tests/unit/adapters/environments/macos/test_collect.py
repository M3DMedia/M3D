"""Tests for macOS environment collection."""

from __future__ import annotations

import platform

import pytest

from m3d.adapters.environments.macos import MacOSEnvironmentPlugin

pytestmark = pytest.mark.macos


def test_collect_returns_host_information() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    result = plugin.collect("host")

    assert result["target"] == "host"
    assert result["hostname"] == (platform.node() or "unknown-host")
    assert result["system"] == "Darwin"
    assert result["release"] == platform.release()
    assert result["machine"] == platform.machine()


def test_collect_reports_processor_information() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    result = plugin.collect("host")

    assert result["processor"] == platform.processor()


def test_collect_reports_system_information() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    result = plugin.collect("host")

    assert result["architecture"] == platform.machine()
    assert isinstance(result["cpu_count"], int)
    assert result["cpu_count"] > 0
    assert isinstance(result["memory_total_bytes"], int)
    assert result["memory_total_bytes"] > 0
    assert isinstance(result["uptime_seconds"], float)
    assert result["uptime_seconds"] >= 0


def test_collect_reports_hardware_information() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    result = plugin.collect("host")

    hardware = result["hardware"]

    assert isinstance(hardware, dict)
    assert hardware["model_name"]
    assert hardware["model_identifier"]
    assert hardware["chip"]
    assert hardware["core_count"]
    assert hardware["memory"]


def test_collect_reports_software_information() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    result = plugin.collect("host")

    software = result["software"]

    assert isinstance(software, dict)
    assert software["product_name"] == "macOS"
    assert software["product_version"]
    assert software["build_version"]


def test_collect_reports_storage_information() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    result = plugin.collect("host")

    storage = result["storage"]

    assert isinstance(storage, dict)
    assert storage["mount_point"] == "/"
    assert isinstance(storage["total_bytes"], int)
    assert isinstance(storage["used_bytes"], int)
    assert isinstance(storage["free_bytes"], int)
    assert isinstance(storage["usage_percent"], float)
    assert storage["total_bytes"] > 0
    assert storage["used_bytes"] >= 0
    assert storage["free_bytes"] >= 0
    assert 0 <= storage["usage_percent"] <= 100


def test_collect_rejects_empty_target() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    with pytest.raises(ValueError, match="Collection target cannot be empty"):
        plugin.collect(" ")


def test_collect_rejects_unsupported_target() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    with pytest.raises(ValueError, match="Unsupported collection target: process"):
        plugin.collect("process")
