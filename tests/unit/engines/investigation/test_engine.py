"""Tests for the investigation orchestration engine."""

from collections.abc import Sequence

from m3d.adapters.event_bus.memory import InMemoryEventBus
from m3d.adapters.storage.memory import InMemoryInvestigationStore
from m3d.domain.common.types import (
    EnvironmentId,
    EventId,
    HypothesisId,
    InvestigationId,
)
from m3d.domain.entity import Entity
from m3d.domain.event import Event
from m3d.domain.evidence import Evidence
from m3d.domain.hypothesis import Hypothesis
from m3d.domain.investigation import Investigation
from m3d.engines.investigation import InvestigationEngine
from m3d.ports.environment import EnvironmentPlugin
from m3d.ports.reasoning import ReasoningProvider


class FakeEnvironment(EnvironmentPlugin):
    """Minimal environment plugin for engine tests."""

    def __init__(self, environment_id: str = "env_test") -> None:
        self.environment_id = EnvironmentId(environment_id)

    def identify(self) -> EnvironmentId:
        return self.environment_id

    def discover(self) -> list[Entity]:
        return []

    def observe(self) -> list[Event]:
        return []

    def collect(self, target: str) -> dict[str, object]:
        return {"target": target}

    def execute(
        self,
        operation: str,
        parameters: dict[str, object],
    ) -> dict[str, object]:
        return {"operation": operation, "parameters": parameters}

    def verify(
        self,
        target: str,
        expected_outcome: str,
    ) -> dict[str, object]:
        return {
            "target": target,
            "expected_outcome": expected_outcome,
        }


class FakeReasoningProvider(ReasoningProvider):
    """Deterministic reasoning provider for engine tests."""

    def generate_hypotheses(
        self,
        investigation: Investigation,
        evidence: Sequence[Evidence],
    ) -> list[Hypothesis]:
        return [
            Hypothesis(
                id=HypothesisId("hyp_test"),
                investigation_id=investigation.id,
                statement="The service is unavailable because its process stopped.",
                confidence=0.8,
            )
        ]

    def evaluate_evidence(
        self,
        investigation: Investigation,
        hypothesis: Hypothesis,
        evidence: Sequence[Evidence],
    ) -> float:
        return 0.8

    def propose_investigation_step(
        self,
        investigation: Investigation,
        hypothesis: Hypothesis,
        evidence: Sequence[Evidence],
    ) -> str:
        return "Check whether the service process is running."

    def evaluate_result(
        self,
        investigation: Investigation,
        hypothesis: Hypothesis,
        evidence: Sequence[Evidence],
    ) -> str:
        return "The evidence supports the hypothesis."

    def generate_conclusion(
        self,
        investigation: Investigation,
        evidence: Sequence[Evidence],
        hypotheses: Sequence[Hypothesis],
    ) -> str:
        return "The service process stopped."


def make_engine(
    environment_id: str = "env_test",
) -> tuple[InvestigationEngine, InMemoryInvestigationStore, InMemoryEventBus]:
    store = InMemoryInvestigationStore()
    event_bus = InMemoryEventBus()
    environment = FakeEnvironment(environment_id)
    reasoning = FakeReasoningProvider()
    engine = InvestigationEngine(
        store=store,
        environment=environment,
        event_bus=event_bus,
        reasoning=reasoning,
    )
    return engine, store, event_bus


def make_event(
    event_type: str = "service_down",
    environment_id: EnvironmentId | None = None,
) -> Event:
    if environment_id is None:
        environment_id = EnvironmentId("env_test")
    from datetime import UTC, datetime

    return Event(
        id=EventId("event_test"),
        timestamp=datetime.now(UTC),
        environment_id=environment_id,
        entity_id=None,
        type=event_type,
        severity="high",
        source="test",
        previous_state="running",
        new_state="down",
        correlation_id="correlation_test",
    )


def test_create_persists_investigation() -> None:
    engine, store, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_test"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    assert investigation.id == InvestigationId("inv_test")
    assert investigation.environment_id == EnvironmentId("env_test")
    assert investigation.trigger == "service_alert"
    assert investigation.objective == "Determine why the service is unavailable."
    assert store.get_investigation("inv_test") == investigation


def test_create_uses_environment_identity() -> None:
    engine, _, _ = make_engine("env_production")
    investigation = engine.create(
        investigation_id=InvestigationId("inv_test"),
        trigger="event",
        objective="Investigate the event.",
    )
    assert investigation.environment_id == EnvironmentId("env_production")


def test_get_returns_persisted_investigation() -> None:
    engine, _, _ = make_engine()
    created = engine.create(
        investigation_id=InvestigationId("inv_test"),
        trigger="event",
        objective="Investigate the event.",
    )
    assert engine.get(created.id) == created


def test_get_missing_investigation_returns_none() -> None:
    engine, _, _ = make_engine()
    assert engine.get(InvestigationId("missing")) is None


def test_subscribed_event_creates_investigation() -> None:
    engine, store, event_bus = make_engine()
    engine.subscribe_to_event(
        event_type="service_down",
        objective="Determine why the service is unavailable.",
    )
    event_bus.publish(make_event())

    investigations = store.get_decisions("inv_test")
    assert investigations == []

    stored = [
        investigation
        for investigation in store._investigations.values()
        if investigation.trigger == "service_down"
    ]
    assert len(stored) == 1
    assert stored[0].trigger == "service_down"
    assert stored[0].objective == "Determine why the service is unavailable."
    assert stored[0].environment_id == EnvironmentId("env_test")


def test_unrelated_event_does_not_create_investigation() -> None:
    engine, store, event_bus = make_engine()
    engine.subscribe_to_event(
        event_type="service_down",
        objective="Investigate service failure.",
    )
    event_bus.publish(make_event(event_type="cpu_high"))

    stored = [
        investigation
        for investigation in store._investigations.values()
        if investigation.trigger == "service_down"
    ]
    assert stored == []


def test_subscribe_to_event_rejects_empty_event_type() -> None:
    engine, _, _ = make_engine()
    try:
        engine.subscribe_to_event(
            event_type=" ",
            objective="Investigate the event.",
        )
    except ValueError as exc:
        assert str(exc) == "Event type cannot be empty."
    else:
        raise AssertionError("Expected ValueError")


def test_subscribe_to_event_rejects_empty_objective() -> None:
    engine, _, _ = make_engine()
    try:
        engine.subscribe_to_event(
            event_type="service_down",
            objective=" ",
        )
    except ValueError as exc:
        assert str(exc) == "Investigation objective cannot be empty."
    else:
        raise AssertionError("Expected ValueError")


def test_collect_evidence_collects_and_persists_result() -> None:
    engine, store, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_test"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    evidence = engine.collect_evidence(
        investigation_id=investigation.id,
        target="service:nginx",
        collection_method="environment.collect",
    )
    assert evidence.investigation_id == investigation.id
    assert evidence.source == "FakeEnvironment"
    assert evidence.observation == "{'target': 'service:nginx'}"
    assert evidence.collection_method == "environment.collect"
    assert evidence.entity_id is None
    assert evidence.metadata["target"] == "service:nginx"
    assert evidence.metadata["collection_result"] == {"target": "service:nginx"}
    assert store.get_evidence(str(investigation.id)) == [evidence]


def test_collect_evidence_associates_entity() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_test"),
        trigger="service_alert",
        objective="Investigate the service.",
    )
    evidence = engine.collect_evidence(
        investigation_id=investigation.id,
        target="service:nginx",
        collection_method="environment.collect",
        entity_id="entity_nginx",
    )
    assert evidence.entity_id is not None
    assert str(evidence.entity_id) == "entity_nginx"


def test_collect_evidence_rejects_missing_investigation() -> None:
    engine, _, _ = make_engine()
    try:
        engine.collect_evidence(
            investigation_id=InvestigationId("missing"),
            target="service:nginx",
            collection_method="environment.collect",
        )
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_collect_evidence_rejects_empty_target() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_test"),
        trigger="service_alert",
        objective="Investigate the service.",
    )
    try:
        engine.collect_evidence(
            investigation_id=investigation.id,
            target=" ",
            collection_method="environment.collect",
        )
    except ValueError as exc:
        assert str(exc) == "Evidence target cannot be empty."
    else:
        raise AssertionError("Expected ValueError")


def test_collect_evidence_rejects_empty_collection_method() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_test"),
        trigger="service_alert",
        objective="Investigate the service.",
    )
    try:
        engine.collect_evidence(
            investigation_id=investigation.id,
            target="service:nginx",
            collection_method=" ",
        )
    except ValueError as exc:
        assert str(exc) == "Collection method cannot be empty."
    else:
        raise AssertionError("Expected ValueError")


def test_generate_hypotheses_uses_evidence_and_persists_results() -> None:
    engine, store, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_test"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    evidence = engine.collect_evidence(
        investigation_id=investigation.id,
        target="service:nginx",
        collection_method="environment.collect",
    )

    hypotheses = engine.generate_hypotheses(investigation.id)

    assert len(hypotheses) == 1
    assert hypotheses[0].id == HypothesisId("hyp_test")
    assert hypotheses[0].investigation_id == investigation.id
    assert hypotheses[0].statement == ("The service is unavailable because its process stopped.")
    assert hypotheses[0].confidence == 0.8
    assert store.get_hypotheses(str(investigation.id)) == hypotheses
    assert store.get_evidence(str(investigation.id)) == [evidence]


def test_generate_hypotheses_rejects_missing_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.generate_hypotheses(InvestigationId("missing"))
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_scope_transitions_and_persists_investigation() -> None:
    engine, store, _ = make_engine()

    investigation = engine.create(
        investigation_id=InvestigationId("inv_scope"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    scoped = engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )

    assert scoped.id == investigation.id
    assert scoped.status == "scoping"
    assert scoped.scope == ("service:nginx", "host")
    assert store.get_investigation(str(investigation.id)) == scoped


def test_scope_rejects_missing_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.scope(
            investigation_id=InvestigationId("missing"),
            scope=("host",),
        )
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_scope_rejects_empty_scope() -> None:
    engine, _, _ = make_engine()

    investigation = engine.create(
        investigation_id=InvestigationId("inv_scope"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    try:
        engine.scope(
            investigation_id=investigation.id,
            scope=(),
        )
    except ValueError as exc:
        assert str(exc) == "Investigation scope cannot be empty."
    else:
        raise AssertionError("Expected ValueError")


def test_start_collection_transitions_and_persists_investigation() -> None:
    engine, store, _ = make_engine()

    investigation = engine.create(
        investigation_id=InvestigationId("inv_collect"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    scoped = engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )

    collecting = engine.start_collection(scoped.id)

    assert collecting.id == scoped.id
    assert collecting.status == "collecting"
    assert collecting.scope == scoped.scope
    assert store.get_investigation(str(scoped.id)) == collecting


def test_start_collection_rejects_missing_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.start_collection(InvestigationId("missing"))
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_start_collection_requires_scoping_state() -> None:
    engine, _, _ = make_engine()

    investigation = engine.create(
        investigation_id=InvestigationId("inv_collect"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    try:
        engine.start_collection(investigation.id)
    except ValueError as exc:
        assert str(exc) == "Invalid investigation transition: created -> collecting"
    else:
        raise AssertionError("Expected ValueError")


def test_start_analysis_transitions_and_persists_investigation() -> None:
    engine, store, _ = make_engine()

    investigation = engine.create(
        investigation_id=InvestigationId("inv_analysis"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    scoped = engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    collecting = engine.start_collection(scoped.id)
    analyzing = engine.start_analysis(collecting.id)

    assert analyzing.id == collecting.id
    assert analyzing.status == "analyzing"
    assert analyzing.scope == collecting.scope
    assert store.get_investigation(str(collecting.id)) == analyzing


def test_start_analysis_rejects_missing_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.start_analysis(InvestigationId("missing"))
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_start_analysis_requires_collecting_state() -> None:
    engine, _, _ = make_engine()

    investigation = engine.create(
        investigation_id=InvestigationId("inv_analysis"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    try:
        engine.start_analysis(investigation.id)
    except ValueError as exc:
        assert str(exc) == "Invalid investigation transition: created -> analyzing"
    else:
        raise AssertionError("Expected ValueError")
