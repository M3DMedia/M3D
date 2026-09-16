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


def _env_info() -> None:
    """Display information about the local macOS environment."""
    environment = MacOSEnvironmentPlugin()
    environment_id = environment.identify()
    print(f"Environment: {environment_id}")


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
