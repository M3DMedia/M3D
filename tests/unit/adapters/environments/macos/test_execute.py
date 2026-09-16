"""Tests for macOS environment execution."""

from __future__ import annotations

import platform

import pytest

from m3d.adapters.environments.macos import MacOSEnvironmentPlugin


def test_execute_get_hostname() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    result = plugin.execute("get_hostname", {})

    assert result["operation"] == "get_hostname"
    assert result["hostname"] == (platform.node() or "unknown-host")


def test_execute_rejects_empty_operation() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    with pytest.raises(ValueError, match="Operation cannot be empty"):
        plugin.execute(" ", {})


def test_execute_rejects_unsupported_operation() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    with pytest.raises(ValueError, match="Unsupported operation: restart"):
        plugin.execute("restart", {})


def test_execute_rejects_unexpected_parameters() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    with pytest.raises(
        ValueError,
        match="Operation get_hostname does not accept parameters",
    ):
        plugin.execute("get_hostname", {"value": "unexpected"})


def test_execute_returns_current_hostname_each_time() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    first = plugin.execute("get_hostname", {})
    second = plugin.execute("get_hostname", {})

    assert first["hostname"] == second["hostname"]
