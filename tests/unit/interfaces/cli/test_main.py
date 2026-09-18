from unittest.mock import patch

from m3d.interfaces.cli.main import _env_info


def _sample_details() -> dict[str, object]:
    return {
        "hostname": "test-mac.local",
        "system": "Darwin",
        "release": "25.6.0",
        "machine": "arm64",
        "processor": "arm",
        "architecture": "arm64",
        "cpu_count": 8,
        "memory_total_bytes": 8589934592,
        "uptime_seconds": 3661,
        "hardware": {
            "model_name": "MacBook Air",
            "chip": "Apple M2",
        },
        "software": {
            "product_name": "macOS",
            "product_version": "26.6.2",
            "build_version": "25G83",
        },
        "network": {
            "interfaces": [
                {
                    "name": "lo0",
                    "status": "active",
                    "ipv4_addresses": ["127.0.0.1"],
                    "ipv6_addresses": ["::1"],
                },
                {
                    "name": "en0",
                    "status": "active",
                    "ipv4_addresses": ["192.168.0.201"],
                    "ipv6_addresses": ["fe80::1"],
                },
            ],
            "default_gateway": "192.168.0.1",
            "dns_servers": ["192.168.0.1"],
        },
        "updates": {
            "status": "updates_available",
            "available_count": 2,
            "updates": [
                {
                    "label": "Safari27.0TahoeAuto-27.0",
                    "title": "Safari",
                    "version": "27.0",
                    "size_bytes": 255452160,
                    "recommended": True,
                    "action": None,
                },
                {
                    "label": "macOS Tahoe 26.7-25G229",
                    "title": "macOS Tahoe 26.7",
                    "version": "26.7",
                    "size_bytes": 3031400448,
                    "recommended": True,
                    "action": "restart",
                },
            ],
        },
        "storage": {
            "mount_point": "/",
            "total_bytes": 245107195904,
            "used_bytes": 186040623104,
            "free_bytes": 59066572800,
            "usage_percent": 75.9,
        },
    }


def test_env_info_displays_updates(capsys) -> None:
    with (
        patch(
            "m3d.interfaces.cli.main.MacOSEnvironmentPlugin.collect",
            return_value=_sample_details(),
        ),
        patch(
            "m3d.interfaces.cli.main.MacOSEnvironmentPlugin.identify",
            return_value="macos_test",
        ),
    ):
        _env_info()

    output = capsys.readouterr().out

    assert "UPDATES" in output
    assert "status: updates_available" in output
    assert "available: 2" in output
    assert "Safari" in output
    assert "version: 27.0" in output
    assert "size: 243.6 MB" in output
    assert "recommended: yes" in output
    assert "macOS Tahoe 26.7" in output
    assert "version: 26.7" in output
    assert "size: 2.8 GB" in output
    assert "action: restart" in output


def test_env_info_displays_up_to_date_status(capsys) -> None:
    details = _sample_details()
    updates = details["updates"]

    assert isinstance(updates, dict)

    updates["status"] = "up_to_date"
    updates["available_count"] = 0
    updates["updates"] = []

    with (
        patch(
            "m3d.interfaces.cli.main.MacOSEnvironmentPlugin.collect",
            return_value=details,
        ),
        patch(
            "m3d.interfaces.cli.main.MacOSEnvironmentPlugin.identify",
            return_value="macos_test",
        ),
    ):
        _env_info()

    output = capsys.readouterr().out

    assert "UPDATES" in output
    assert "status: up_to_date" in output
    assert "available: 0" in output


def test_env_info_formats_missing_update_metadata(capsys) -> None:
    details = _sample_details()
    updates = details["updates"]

    assert isinstance(updates, dict)

    available_updates = updates["updates"]
    assert isinstance(available_updates, list)

    available_updates[0]["title"] = None
    available_updates[0]["version"] = None
    available_updates[0]["size_bytes"] = None
    available_updates[0]["recommended"] = False
    available_updates[0]["action"] = None

    with (
        patch(
            "m3d.interfaces.cli.main.MacOSEnvironmentPlugin.collect",
            return_value=details,
        ),
        patch(
            "m3d.interfaces.cli.main.MacOSEnvironmentPlugin.identify",
            return_value="macos_test",
        ),
    ):
        _env_info()

    output = capsys.readouterr().out

    assert "Safari27.0TahoeAuto-27.0" in output
    assert "version: unknown" in output
    assert "size: unknown" in output
    assert "recommended: no" in output


def test_env_info_displays_collection_progress(capsys) -> None:
    details = _sample_details()
    progress_messages: list[str] = []

    def collect(target: str, progress=None) -> dict[str, object]:
        assert target == "host"
        assert progress is not None

        for message in (
            "Checking hardware information...",
            "Checking software information...",
            "Checking network interfaces...",
            "Checking default gateway...",
            "Checking DNS configuration...",
            "Checking system updates...",
            "Checking storage...",
        ):
            progress_messages.append(message)
            progress(message)

        return details

    with (
        patch(
            "m3d.interfaces.cli.main.MacOSEnvironmentPlugin.collect",
            side_effect=collect,
        ),
        patch(
            "m3d.interfaces.cli.main.MacOSEnvironmentPlugin.identify",
            return_value="macos_test",
        ),
    ):
        _env_info()

    output = capsys.readouterr().out

    expected_progress = [
        "Checking hardware information... done",
        "Checking software information... done",
        "Checking network interfaces... done",
        "Checking default gateway... done",
        "Checking DNS configuration... done",
        "Checking system updates... done",
        "Checking storage... done",
    ]

    assert progress_messages == [
        message.removesuffix("...")
        + "..."
        for message in progress_messages
    ]

    progress_start = output.index("Checking hardware information...")
    environment_start = output.index("ENVIRONMENT")
    progress_output = output[progress_start:environment_start]

    assert all(message in progress_output for message in expected_progress)
    assert progress_output.index(expected_progress[0]) < progress_output.index(
        expected_progress[1]
    )
    assert progress_output.index(expected_progress[1]) < progress_output.index(
        expected_progress[2]
    )
    assert progress_output.index(expected_progress[2]) < progress_output.index(
        expected_progress[3]
    )
    assert progress_output.index(expected_progress[3]) < progress_output.index(
        expected_progress[4]
    )
    assert progress_output.index(expected_progress[4]) < progress_output.index(
        expected_progress[5]
    )
    assert progress_output.index(expected_progress[5]) < progress_output.index(
        expected_progress[6]
    )
