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

def test_collect_reports_network_information() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    result = plugin.collect("host")
    network = result["network"]

    assert isinstance(network, dict)
    assert isinstance(network["interfaces"], list)
    assert isinstance(network["default_gateway"], (str, type(None)))
    assert isinstance(network["dns_servers"], list)


def test_network_interfaces_have_expected_structure() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    interfaces = plugin._network_interfaces()

    assert isinstance(interfaces, list)

    for interface in interfaces:
        assert isinstance(interface, dict)
        assert isinstance(interface["name"], str)
        assert interface["name"]
        assert interface["status"] in {"active", "inactive", "unknown"}
        assert isinstance(interface["mac_address"], (str, type(None)))
        assert isinstance(interface["ipv4_addresses"], list)
        assert isinstance(interface["ipv6_addresses"], list)


def test_default_gateway_is_string_or_none() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    gateway = plugin._default_gateway()

    assert isinstance(gateway, (str, type(None)))


def test_dns_servers_are_strings() -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    servers = plugin._dns_servers()

    assert isinstance(servers, list)
    assert all(isinstance(server, str) for server in servers)

def test_software_updates_parse_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    software_update_output = """Software Update Tool

Finding available software

Software Update found the following new or updated software:

* Label: Safari27.0TahoeAuto-27.0
    Title: Safari, Version: 27.0, Size: 249465KiB, Recommended: YES,

* Label: macOS Tahoe 26.7-25G229
    Title: macOS Tahoe 26.7, Version: 26.7, Size: 2960352KiB, Recommended: YES, Action: restart,

"""

    monkeypatch.setattr(
        plugin,
        "_run_command",
        lambda command: software_update_output,
    )

    result = plugin._software_updates()

    assert result["status"] == "updates_available"
    assert result["available_count"] == 2

    updates = result["updates"]
    assert isinstance(updates, list)

    safari = updates[0]
    assert safari["label"] == "Safari27.0TahoeAuto-27.0"
    assert safari["title"] == "Safari"
    assert safari["version"] == "27.0"
    assert safari["size_bytes"] == 249465 * 1024
    assert safari["recommended"] is True
    assert safari["action"] is None

    macos = updates[1]
    assert macos["label"] == "macOS Tahoe 26.7-25G229"
    assert macos["title"] == "macOS Tahoe 26.7"
    assert macos["version"] == "26.7"
    assert macos["size_bytes"] == 2960352 * 1024
    assert macos["recommended"] is True
    assert macos["action"] == "restart"


def test_software_updates_report_up_to_date(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plugin = MacOSEnvironmentPlugin("macos_test")

    monkeypatch.setattr(
        plugin,
        "_run_command",
        lambda command: (
            "Software Update Tool\n\n"
            "Finding available software\n\n"
            "No new software available.\n"
        ),
    )

    result = plugin._software_updates()

    assert result["status"] == "up_to_date"
    assert result["available_count"] == 0
    assert result["updates"] == []
