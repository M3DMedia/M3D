"""M3D command-line interface implementation."""

from __future__ import annotations

import argparse

from m3d.adapters.environments.macos import MacOSEnvironmentPlugin


def main() -> None:
    """Run the M3D command-line interface."""
    parser = argparse.ArgumentParser(
        prog="m3d",
        description="Open-source runtime for safe, autonomous AI operations.",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        metavar="COMMAND",
    )

    env_parser = subparsers.add_parser(
        "env",
        help="Inspect and interact with operational environments.",
        description="Inspect and interact with operational environments.",
    )
    env_subparsers = env_parser.add_subparsers(
        dest="env_command",
        title="environment commands",
        metavar="COMMAND",
    )

    info_parser = env_subparsers.add_parser(
        "info",
        help="Show information about the connected environment.",
        description="Show information about the connected environment.",
    )
    info_parser.set_defaults(handler=_env_info)

    list_parser = env_subparsers.add_parser(
        "list",
        help="List entities discovered in the environment.",
        description="List entities discovered in the environment.",
    )
    list_parser.set_defaults(handler=_env_list)

    events_parser = env_subparsers.add_parser(
        "events",
        help="Show events observed from the environment.",
        description="Show events observed from the environment.",
    )
    events_parser.set_defaults(handler=_env_events)

    get_parser = env_subparsers.add_parser(
        "get",
        help="Collect detailed information about an environment target.",
        description="Collect detailed information about an environment target.",
    )
    get_parser.add_argument(
        "target",
        choices=["host"],
        help="Environment target to inspect.",
    )
    get_parser.set_defaults(handler=_env_get)

    args = parser.parse_args()

    handler = getattr(args, "handler", None)
    if handler is _env_get:
        handler(args.target)
    elif handler is not None:
        handler()
    else:
        parser.print_help()


def _format_bytes(value: object) -> str:
    """Format a byte count for human-readable CLI output."""
    if not isinstance(value, int):
        return "unknown"

    units = ("B", "KB", "MB", "GB", "TB", "PB")
    size = float(value)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024

    return f"{size:.1f} PB"


def _format_uptime(value: object) -> str:
    """Format uptime seconds for human-readable CLI output."""
    if not isinstance(value, (int, float)):
        return "unknown"

    total_seconds = max(0, int(value))
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts: list[str] = []

    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return ", ".join(parts)


def _env_info() -> None:
    """Display detailed information about the local macOS environment."""
    environment = MacOSEnvironmentPlugin()
    details = environment.collect("host")

    print("ENVIRONMENT")
    print(f"  id: {environment.identify()}")
    print()

    print("HOST")
    print(f"  hostname: {details['hostname']}")
    print(f"  system: {details['system']}")
    print(f"  release: {details['release']}")
    print(f"  machine: {details['machine']}")
    print(f"  processor: {details['processor']}")
    print(f"  architecture: {details['architecture']}")
    print(f"  logical_cpus: {details['cpu_count']}")
    print(f"  memory: {_format_bytes(details['memory_total_bytes'])}")
    print(f"  uptime: {_format_uptime(details['uptime_seconds'])}")
    print()

    hardware = details["hardware"]
    if isinstance(hardware, dict):
        print("HARDWARE")
        for key, value in hardware.items():
            print(f"  {key}: {value}")
        print()

    software = details["software"]
    if isinstance(software, dict):
        print("SOFTWARE")
        for key, value in software.items():
            print(f"  {key}: {value}")
        print()

    storage = details["storage"]
    if isinstance(storage, dict):
        print("STORAGE")
        print(f"  mount_point: {storage['mount_point']}")
        print(f"  total: {_format_bytes(storage['total_bytes'])}")
        print(f"  used: {_format_bytes(storage['used_bytes'])}")
        print(f"  free: {_format_bytes(storage['free_bytes'])}")
        print(f"  usage: {storage['usage_percent']}%")



def _env_list() -> None:
    """List entities discovered in the local macOS environment."""
    environment = MacOSEnvironmentPlugin()
    entities = environment.discover()

    for entity in entities:
        print(entity.type.upper())
        print(f"  id: {entity.id}")
        print(f"  name: {entity.name}")
        print(f"  status: {entity.status}")


def _env_events() -> None:
    """Show events observed from the local macOS environment."""
    environment = MacOSEnvironmentPlugin()
    events = environment.observe()

    for event in events:
        print("EVENT")
        print(f"  id: {event.id}")
        print(f"  type: {event.type}")
        print(f"  severity: {event.severity}")
        print(f"  entity: {event.entity_id}")
        print(f"  source: {event.source}")
        print(f"  timestamp: {event.timestamp}")


def _env_get(target: str) -> None:
    """Collect detailed information about a local macOS target."""
    environment = MacOSEnvironmentPlugin()
    details = environment.collect(target)

    print(target.upper())
    for key, value in details.items():
        if key == "target":
            continue
        print(f"  {key}: {value}")
