"""Tests for macOS environment verification."""

from __future__ import annotations

import pytest

from m3d.adapters.environments.macos import MacOSEnvironmentPlugin


def test_verify_host_present() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    result = plugin.verify("host", "host_present")

    assert result["target"] == "host"
    assert result["expected_outcome"] == "host_present"
    assert result["verified"] is True
    assert result["observed_outcome"] == "host_present"


def test_verify_host_online() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    result = plugin.verify("host", "host_online")

    assert result["target"] == "host"
    assert result["expected_outcome"] == "host_online"
    assert result["verified"] is True
    assert result["observed_outcome"] == "host_online"


def test_verify_rejects_empty_target() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    with pytest.raises(ValueError, match="Verification target cannot be empty"):
        plugin.verify(" ", "host_present")


def test_verify_rejects_empty_expected_outcome() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    with pytest.raises(ValueError, match="Expected outcome cannot be empty"):
        plugin.verify("host", " ")


def test_verify_rejects_unsupported_target() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    with pytest.raises(ValueError, match="Unsupported verification target: process"):
        plugin.verify("process", "host_present")


def test_verify_rejects_unsupported_expected_outcome() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    with pytest.raises(
        ValueError,
        match="Unsupported expected outcome: process_running",
    ):
        plugin.verify("host", "process_running")
