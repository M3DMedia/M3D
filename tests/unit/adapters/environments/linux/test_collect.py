"""Tests for Linux environment collection."""

from __future__ import annotations

import platform

import pytest

from m3d.adapters.environments.linux import LinuxEnvironmentPlugin


def test_collect_host_returns_platform_information() -> None:
    plugin = LinuxEnvironmentPlugin()

    result = plugin.collect("host")

    assert result["target"] == "host"
    assert result["hostname"] == (platform.node() or "unknown-host")
    assert result["system"] == platform.system()
    assert result["release"] == platform.release()
    assert result["machine"] == platform.machine()
    assert result["processor"] == platform.processor()


def test_collect_host_returns_expected_keys() -> None:
    plugin = LinuxEnvironmentPlugin()

    result = plugin.collect("host")

    assert set(result) == {
        "target",
        "hostname",
        "system",
        "release",
        "machine",
        "processor",
    }


def test_collect_rejects_unsupported_target() -> None:
    plugin = LinuxEnvironmentPlugin()

    with pytest.raises(ValueError, match="Unsupported collection target"):
        plugin.collect("unsupported")


def test_collect_rejects_empty_target() -> None:
    plugin = LinuxEnvironmentPlugin()

    with pytest.raises(ValueError, match="Collection target cannot be empty"):
        plugin.collect(" ")
