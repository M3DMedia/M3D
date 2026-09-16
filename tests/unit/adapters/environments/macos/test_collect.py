"""Tests for macOS environment collection."""

from __future__ import annotations

import platform

import pytest

from m3d.adapters.environments.macos import MacOSEnvironmentPlugin


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


def test_collect_rejects_empty_target() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    with pytest.raises(ValueError, match="Collection target cannot be empty"):
        plugin.collect(" ")


def test_collect_rejects_unsupported_target() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    with pytest.raises(ValueError, match="Unsupported collection target: process"):
        plugin.collect("process")
