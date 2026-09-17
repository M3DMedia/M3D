import pytest

from m3d.adapters.environments.macos import MacOSEnvironmentPlugin

pytestmark = pytest.mark.macos

def test_macos_environment_smoke() -> None:
    plugin = MacOSEnvironmentPlugin()

    environment_id = plugin.identify()
    entities = plugin.discover()
    events = plugin.observe()
    collection = plugin.collect("host")
    execution = plugin.execute("get_hostname", {})
    host_present = plugin.verify("host", "host_present")
    host_online = plugin.verify("host", "host_online")

    assert str(environment_id) == "macos_local"

    assert len(entities) == 1
    host = entities[0]
    assert host.environment_id == environment_id
    assert host.type == "host"
    assert host.status == "online"

    assert len(events) == 1
    event = events[0]
    assert event.environment_id == environment_id
    assert event.entity_id == host.id
    assert event.type == "host.observed"

    assert collection["target"] == "host"
    assert collection["hostname"] == host.name
    assert collection["system"] == "Darwin"

    assert execution["operation"] == "get_hostname"
    assert execution["hostname"] == host.name

    assert host_present["verified"] is True
    assert host_online["verified"] is True
