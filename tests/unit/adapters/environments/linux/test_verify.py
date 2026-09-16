"""Tests for Linux environment verification."""

from __future__ import annotations

import pytest

from m3d.adapters.environments.linux import LinuxEnvironmentPlugin


def test_verify_host_present() -> None:
    plugin = LinuxEnvironmentPlugin()

    result = plugin.verify("host", "host_present")

    assert result["target"] == "host"
    assert result["expected_outcome"] == "host_present"
    assert result["verified"] is True
    assert result["observed_outcome"] == "host_present"
    assert result["reason"] == "Host is present."


def test_verify_host_online() -> None:
    plugin = LinuxEnvironmentPlugin()

    result = plugin.verify("host", "host_online")

    assert result["target"] == "host"
    assert result["expected_outcome"] == "host_online"
    assert result["verified"] is True
    assert result["observed_outcome"] == "host_online"
    assert result["reason"] == "Host is online."


def test_verify_rejects_empty_target() -> None:
    plugin = LinuxEnvironmentPlugin()

    with pytest.raises(ValueError, match="Verification target cannot be empty"):
        plugin.verify(" ", "host_present")


def test_verify_rejects_empty_expected_outcome() -> None:
    plugin = LinuxEnvironmentPlugin()

    with pytest.raises(ValueError, match="Expected outcome cannot be empty"):
        plugin.verify("host", " ")


def test_verify_rejects_unsupported_target() -> None:
    plugin = LinuxEnvironmentPlugin()

    with pytest.raises(ValueError, match="Unsupported verification target"):
        plugin.verify("process", "running")


def test_verify_rejects_unsupported_outcome() -> None:
    plugin = LinuxEnvironmentPlugin()

    with pytest.raises(ValueError, match="Unsupported expected outcome"):
        plugin.verify("host", "unknown")
