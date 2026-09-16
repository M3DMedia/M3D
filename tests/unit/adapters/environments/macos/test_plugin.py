"""Tests for the macOS environment adapter."""

from __future__ import annotations

import pytest

from m3d.adapters.environments.macos import MacOSEnvironmentPlugin
from m3d.domain.common.types import EnvironmentId


def test_identify_returns_configured_environment_id() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    assert plugin.identify() == EnvironmentId("macos_test")


def test_identify_uses_default_environment_id() -> None:
    plugin = MacOSEnvironmentPlugin()

    assert plugin.identify() == EnvironmentId("macos_local")


def test_empty_environment_id_is_rejected() -> None:
    with pytest.raises(ValueError, match="Environment ID cannot be empty"):
        MacOSEnvironmentPlugin(" ")


def test_environment_id_is_stable() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    assert plugin.identify() == plugin.identify()
