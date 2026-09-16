"""Tests for Linux environment execution."""

from __future__ import annotations

import platform

import pytest

from m3d.adapters.environments.linux import LinuxEnvironmentPlugin


def test_execute_get_hostname() -> None:
    plugin = LinuxEnvironmentPlugin()

    result = plugin.execute("get_hostname", {})

    assert result["operation"] == "get_hostname"
    assert result["hostname"] == (platform.node() or "unknown-host")


def test_execute_get_hostname_returns_expected_keys() -> None:
    plugin = LinuxEnvironmentPlugin()

    result = plugin.execute("get_hostname", {})

    assert set(result) == {"operation", "hostname"}


def test_execute_rejects_empty_operation() -> None:
    plugin = LinuxEnvironmentPlugin()

    with pytest.raises(ValueError, match="Operation cannot be empty"):
        plugin.execute(" ", {})


def test_execute_rejects_unsupported_operation() -> None:
    plugin = LinuxEnvironmentPlugin()

    with pytest.raises(ValueError, match="Unsupported operation"):
        plugin.execute("shell", {})


def test_execute_get_hostname_rejects_parameters() -> None:
    plugin = LinuxEnvironmentPlugin()

    with pytest.raises(ValueError, match="does not accept parameters"):
        plugin.execute("get_hostname", {"command": "hostname"})
