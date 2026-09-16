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


def test_start_hypothesis_generation_transitions_and_persists_investigation() -> None:
    engine, store, _ = make_engine()

    investigation = engine.create(
        investigation_id=InvestigationId("inv_hypothesis"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    scoped = engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    collecting = engine.start_collection(scoped.id)
    analyzing = engine.start_analysis(collecting.id)
    hypothesis = engine.start_hypothesis_generation(analyzing.id)

    assert hypothesis.id == analyzing.id
    assert hypothesis.status == "hypothesis"
    assert hypothesis.scope == analyzing.scope
    assert store.get_investigation(str(analyzing.id)) == hypothesis


def test_start_hypothesis_generation_rejects_missing_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.start_hypothesis_generation(InvestigationId("missing"))
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_start_hypothesis_generation_requires_analyzing_state() -> None:
    engine, _, _ = make_engine()

    investigation = engine.create(
        investigation_id=InvestigationId("inv_hypothesis"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    try:
        engine.start_hypothesis_generation(investigation.id)
    except ValueError as exc:
        assert str(exc) == "Invalid investigation transition: created -> hypothesis"
    else:
        raise AssertionError("Expected ValueError")


def test_start_testing_transitions_and_persists_investigation() -> None:
    engine, store, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_testing"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    scoped = engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    collecting = engine.start_collection(scoped.id)
    analyzing = engine.start_analysis(collecting.id)
    hypothesis = engine.start_hypothesis_generation(analyzing.id)
    testing = engine.start_testing(hypothesis.id)

    assert testing.id == hypothesis.id
    assert testing.status == "testing"
    assert testing.scope == hypothesis.scope
    assert store.get_investigation(str(hypothesis.id)) == testing


def test_start_testing_rejects_missing_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.start_testing(InvestigationId("missing"))
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_start_testing_requires_hypothesis_state() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_testing"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    try:
        engine.start_testing(investigation.id)
    except ValueError as exc:
        assert str(exc) == "Invalid investigation transition: created -> testing"
    else:
        raise AssertionError("Expected ValueError")


def test_start_conclusion_transitions_and_persists_investigation() -> None:
    engine, store, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_conclusion"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    scoped = engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    collecting = engine.start_collection(scoped.id)
    analyzing = engine.start_analysis(collecting.id)
    hypothesis = engine.start_hypothesis_generation(analyzing.id)
    testing = engine.start_testing(hypothesis.id)
    conclusion = engine.start_conclusion(testing.id)

    assert conclusion.id == testing.id
    assert conclusion.status == "conclusion"
    assert conclusion.scope == testing.scope
    assert store.get_investigation(str(testing.id)) == conclusion


def test_start_conclusion_rejects_missing_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.start_conclusion(InvestigationId("missing"))
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_start_conclusion_requires_testing_state() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_conclusion"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    try:
        engine.start_conclusion(investigation.id)
    except ValueError as exc:
        assert str(exc) == "Invalid investigation transition: created -> conclusion"
    else:
        raise AssertionError("Expected ValueError")


def test_generate_conclusion_generates_and_persists() -> None:
    engine, store, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_generate_conclusion"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    scoped = engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    collecting = engine.start_collection(scoped.id)
    analyzing = engine.start_analysis(collecting.id)
    hypothesis = engine.start_hypothesis_generation(analyzing.id)
    testing = engine.start_testing(hypothesis.id)
    conclusion = engine.start_conclusion(testing.id)

    generated = engine.generate_conclusion(conclusion.id)

    assert generated.id == conclusion.id
    assert generated.status == "conclusion"
    assert generated.conclusion == "The service process stopped."
    assert store.get_investigation(str(conclusion.id)) == generated


def test_generate_conclusion_rejects_missing_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.generate_conclusion(InvestigationId("missing"))
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_generate_conclusion_requires_conclusion_state() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_generate_conclusion_state"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    try:
        engine.generate_conclusion(investigation.id)
    except ValueError as exc:
        assert str(exc) == "Investigation must be in conclusion state."
    else:
        raise AssertionError("Expected ValueError")


def test_generate_conclusion_rejects_empty_conclusion() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_generate_empty_conclusion"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    scoped = engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    collecting = engine.start_collection(scoped.id)
    analyzing = engine.start_analysis(collecting.id)
    hypothesis = engine.start_hypothesis_generation(analyzing.id)
    testing = engine.start_testing(hypothesis.id)
    conclusion = engine.start_conclusion(testing.id)

    engine._reasoning.generate_conclusion = lambda *_args: "   "

    try:
        engine.generate_conclusion(conclusion.id)
    except ValueError as exc:
        assert str(exc) == "Investigation conclusion cannot be empty."
    else:
        raise AssertionError("Expected ValueError")


def test_complete_transitions_and_persists_investigation() -> None:
    engine, store, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_completed"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    scoped = engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    collecting = engine.start_collection(scoped.id)
    analyzing = engine.start_analysis(collecting.id)
    hypothesis = engine.start_hypothesis_generation(analyzing.id)
    testing = engine.start_testing(hypothesis.id)
    conclusion = engine.start_conclusion(testing.id)
    conclusion = engine.generate_conclusion(conclusion.id)
    completed = engine.complete(conclusion.id)

    assert completed.id == conclusion.id
    assert completed.status == "completed"
    assert completed.scope == conclusion.scope
    assert store.get_investigation(str(conclusion.id)) == completed


def test_complete_rejects_missing_conclusion() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_missing_conclusion"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    scoped = engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    collecting = engine.start_collection(scoped.id)
    analyzing = engine.start_analysis(collecting.id)
    hypothesis = engine.start_hypothesis_generation(analyzing.id)
    testing = engine.start_testing(hypothesis.id)
    conclusion = engine.start_conclusion(testing.id)

    try:
        engine.complete(conclusion.id)
    except ValueError as exc:
        assert str(exc) == "Investigation conclusion is required before completion."
    else:
        raise AssertionError("Expected ValueError")


def test_propose_decision_persists_proposed_decision() -> None:
    engine, store, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_decision"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    scoped = engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    collecting = engine.start_collection(scoped.id)
    evidence = engine.collect_evidence(
        investigation_id=collecting.id,
        target="host",
        collection_method="system_inspection",
    )
    analyzing = engine.start_analysis(collecting.id)
    hypothesis = engine.start_hypothesis_generation(analyzing.id)
    testing = engine.start_testing(hypothesis.id)
    conclusion = engine.start_conclusion(testing.id)
    conclusion = engine.generate_conclusion(conclusion.id)
    completed = engine.complete(conclusion.id)

    decision = engine.propose_decision(
        investigation_id=completed.id,
        decision="Restart the affected service.",
        rationale=completed.conclusion or "",
        confidence=0.9,
    )

    assert str(decision.id).startswith("decision_")
    assert decision.investigation_id == completed.id
    assert decision.decision == "Restart the affected service."
    assert decision.rationale == completed.conclusion
    assert decision.evidence_ids == (evidence.id,)
    assert decision.confidence == 0.9
    assert decision.status == "proposed"
    assert store.get_decisions(str(completed.id)) == [decision]


def test_propose_decision_requires_completed_investigation() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_incomplete_decision"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    try:
        engine.propose_decision(
            investigation_id=investigation.id,
            decision="Restart the affected service.",
            rationale="The service process stopped.",
        )
    except ValueError as exc:
        assert str(exc) == "Investigation must be completed before proposing a decision."
    else:
        raise AssertionError("Expected ValueError")


def test_complete_rejects_missing_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.complete(InvestigationId("missing"))
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_complete_requires_conclusion_state() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_completed"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    try:
        engine.complete(investigation.id)
    except ValueError as exc:
        assert str(exc) == "Invalid investigation transition: created -> completed"
    else:
        raise AssertionError("Expected ValueError")


def test_get_hypothesis_returns_persisted_hypothesis() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_get_hypothesis"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.collect_evidence(
        investigation_id=investigation.id,
        target="service:nginx",
        collection_method="environment.collect",
    )
    hypotheses = engine.generate_hypotheses(investigation.id)

    assert hypotheses
    assert engine.get_hypothesis(hypotheses[0].id) == hypotheses[0]


def test_get_hypothesis_returns_none_for_unknown_hypothesis() -> None:
    engine, _, _ = make_engine()

    assert engine.get_hypothesis(HypothesisId("missing")) is None


def test_evaluate_hypothesis_uses_persisted_hypothesis_and_evidence() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_evaluate_hypothesis"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    engine.start_collection(investigation.id)
    engine.collect_evidence(
        investigation_id=investigation.id,
        target="service:nginx",
        collection_method="environment.collect",
    )
    engine.start_analysis(investigation.id)
    engine.start_hypothesis_generation(investigation.id)
    hypotheses = engine.generate_hypotheses(investigation.id)
    engine.start_testing(investigation.id)

    score = engine.evaluate_hypothesis(
        investigation_id=investigation.id,
        hypothesis_id=hypotheses[0].id,
    )

    assert score == 0.8


def test_evaluate_hypothesis_rejects_unknown_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.evaluate_hypothesis(
            investigation_id=InvestigationId("missing"),
            hypothesis_id=HypothesisId("hyp_test"),
        )
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_evaluate_hypothesis_rejects_unknown_hypothesis() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_unknown_hypothesis"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    engine.start_collection(investigation.id)
    engine.start_analysis(investigation.id)
    engine.start_hypothesis_generation(investigation.id)
    engine.start_testing(investigation.id)

    try:
        engine.evaluate_hypothesis(
            investigation_id=investigation.id,
            hypothesis_id=HypothesisId("missing"),
        )
    except ValueError as exc:
        assert str(exc) == "Hypothesis not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_evaluate_hypothesis_rejects_hypothesis_from_another_investigation() -> None:
    engine, _, _ = make_engine()
    first = engine.create(
        investigation_id=InvestigationId("inv_first"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    second = engine.create(
        investigation_id=InvestigationId("inv_second"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.collect_evidence(
        investigation_id=first.id,
        target="service:nginx",
        collection_method="environment.collect",
    )
    hypotheses = engine.generate_hypotheses(first.id)
    engine.scope(
        investigation_id=second.id,
        scope=("service:nginx", "host"),
    )
    engine.start_collection(second.id)
    engine.start_analysis(second.id)
    engine.start_hypothesis_generation(second.id)
    engine.start_testing(second.id)

    try:
        engine.evaluate_hypothesis(
            investigation_id=second.id,
            hypothesis_id=hypotheses[0].id,
        )
    except ValueError as exc:
        assert str(exc) == "Hypothesis does not belong to the requested investigation."
    else:
        raise AssertionError("Expected ValueError")


def test_evaluate_hypothesis_requires_testing_state() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_evaluate_state"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.collect_evidence(
        investigation_id=investigation.id,
        target="service:nginx",
        collection_method="environment.collect",
    )
    hypotheses = engine.generate_hypotheses(investigation.id)

    try:
        engine.evaluate_hypothesis(
            investigation_id=investigation.id,
            hypothesis_id=hypotheses[0].id,
        )
    except ValueError as exc:
        assert str(exc) == "Investigation must be in testing state."
    else:
        raise AssertionError("Expected ValueError")


def test_evaluate_result_uses_persisted_hypothesis_and_evidence() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_evaluate_result"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    engine.start_collection(investigation.id)
    engine.collect_evidence(
        investigation_id=investigation.id,
        target="service:nginx",
        collection_method="environment.collect",
    )
    engine.start_analysis(investigation.id)
    engine.start_hypothesis_generation(investigation.id)
    hypotheses = engine.generate_hypotheses(investigation.id)
    engine.start_testing(investigation.id)

    result = engine.evaluate_result(
        investigation_id=investigation.id,
        hypothesis_id=hypotheses[0].id,
    )

    assert result == "The evidence supports the hypothesis."


def test_evaluate_result_rejects_unknown_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.evaluate_result(
            investigation_id=InvestigationId("missing"),
            hypothesis_id=HypothesisId("hyp_test"),
        )
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_evaluate_result_rejects_unknown_hypothesis() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_result_unknown_hypothesis"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    engine.start_collection(investigation.id)
    engine.start_analysis(investigation.id)
    engine.start_hypothesis_generation(investigation.id)
    engine.start_testing(investigation.id)

    try:
        engine.evaluate_result(
            investigation_id=investigation.id,
            hypothesis_id=HypothesisId("missing"),
        )
    except ValueError as exc:
        assert str(exc) == "Hypothesis not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_evaluate_result_rejects_hypothesis_from_another_investigation() -> None:
    engine, _, _ = make_engine()
    first = engine.create(
        investigation_id=InvestigationId("inv_result_first"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    second = engine.create(
        investigation_id=InvestigationId("inv_result_second"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.collect_evidence(
        investigation_id=first.id,
        target="service:nginx",
        collection_method="environment.collect",
    )
    hypotheses = engine.generate_hypotheses(first.id)
    engine.scope(
        investigation_id=second.id,
        scope=("service:nginx", "host"),
    )
    engine.start_collection(second.id)
    engine.start_analysis(second.id)
    engine.start_hypothesis_generation(second.id)
    engine.start_testing(second.id)

    try:
        engine.evaluate_result(
            investigation_id=second.id,
            hypothesis_id=hypotheses[0].id,
        )
    except ValueError as exc:
        assert str(exc) == "Hypothesis does not belong to the requested investigation."
    else:
        raise AssertionError("Expected ValueError")


def test_evaluate_result_requires_testing_state() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_evaluate_result_state"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.collect_evidence(
        investigation_id=investigation.id,
        target="service:nginx",
        collection_method="environment.collect",
    )
    hypotheses = engine.generate_hypotheses(investigation.id)

    try:
        engine.evaluate_result(
            investigation_id=investigation.id,
            hypothesis_id=hypotheses[0].id,
        )
    except ValueError as exc:
        assert str(exc) == "Investigation must be in testing state."
    else:
        raise AssertionError("Expected ValueError")


def test_resolve_hypothesis_persists_supported_state() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_resolve_supported"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    engine.start_collection(investigation.id)
    engine.collect_evidence(
        investigation_id=investigation.id,
        target="service:nginx",
        collection_method="environment.collect",
    )
    engine.start_analysis(investigation.id)
    engine.start_hypothesis_generation(investigation.id)
    hypotheses = engine.generate_hypotheses(investigation.id)
    engine.start_testing(investigation.id)
    engine.resolve_hypothesis(
        investigation_id=investigation.id,
        hypothesis_id=hypotheses[0].id,
        target_status="testing",
    )

    resolved = engine.resolve_hypothesis(
        investigation_id=investigation.id,
        hypothesis_id=hypotheses[0].id,
        target_status="supported",
    )

    assert resolved.status == "supported"
    assert engine.get_hypothesis(hypotheses[0].id) == resolved


def test_resolve_hypothesis_persists_weakened_state() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_resolve_weakened"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    engine.start_collection(investigation.id)
    engine.start_analysis(investigation.id)
    engine.start_hypothesis_generation(investigation.id)
    hypotheses = engine.generate_hypotheses(investigation.id)
    engine.start_testing(investigation.id)
    engine.resolve_hypothesis(
        investigation_id=investigation.id,
        hypothesis_id=hypotheses[0].id,
        target_status="testing",
    )

    resolved = engine.resolve_hypothesis(
        investigation_id=investigation.id,
        hypothesis_id=hypotheses[0].id,
        target_status="weakened",
    )

    assert resolved.status == "weakened"
    assert engine.get_hypothesis(hypotheses[0].id) == resolved


def test_resolve_hypothesis_persists_rejected_state() -> None:
    engine, _, _ = make_engine()
    investigation = engine.create(
        investigation_id=InvestigationId("inv_resolve_rejected"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )
    engine.scope(
        investigation_id=investigation.id,
        scope=("service:nginx", "host"),
    )
    engine.start_collection(investigation.id)
    engine.start_analysis(investigation.id)
    engine.start_hypothesis_generation(investigation.id)
    hypotheses = engine.generate_hypotheses(investigation.id)
    engine.start_testing(investigation.id)
    engine.resolve_hypothesis(
        investigation_id=investigation.id,
        hypothesis_id=hypotheses[0].id,
        target_status="testing",
    )

    resolved = engine.resolve_hypothesis(
        investigation_id=investigation.id,
        hypothesis_id=hypotheses[0].id,
        target_status="rejected",
    )

    assert resolved.status == "rejected"
    assert engine.get_hypothesis(hypotheses[0].id) == resolved

def test_resolve_hypothesis_rejects_unknown_investigation() -> None:
    engine, _, _ = make_engine()

    try:
        engine.resolve_hypothesis(
            investigation_id=InvestigationId("missing"),
            hypothesis_id=HypothesisId("hyp_test"),
            target_status="testing",
        )
    except ValueError as exc:
        assert str(exc) == "Investigation not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_resolve_hypothesis_rejects_unknown_hypothesis() -> None:
    engine, _, _ = make_engine()

    investigation = engine.create(
        investigation_id=InvestigationId("inv_resolve_unknown_hypothesis"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    try:
        engine.resolve_hypothesis(
            investigation_id=investigation.id,
            hypothesis_id=HypothesisId("missing"),
            target_status="testing",
        )
    except ValueError as exc:
        assert str(exc) == "Hypothesis not found: missing"
    else:
        raise AssertionError("Expected ValueError")


def test_resolve_hypothesis_rejects_hypothesis_from_another_investigation() -> None:
    engine, _, _ = make_engine()

    first = engine.create(
        investigation_id=InvestigationId("inv_resolve_first"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    second = engine.create(
        investigation_id=InvestigationId("inv_resolve_second"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    engine.collect_evidence(
        investigation_id=first.id,
        target="service:nginx",
        collection_method="environment.collect",
    )
    hypotheses = engine.generate_hypotheses(first.id)

    try:
        engine.resolve_hypothesis(
            investigation_id=second.id,
            hypothesis_id=hypotheses[0].id,
            target_status="testing",
        )
    except ValueError as exc:
        assert str(exc) == "Hypothesis does not belong to the requested investigation."
    else:
        raise AssertionError("Expected ValueError")


def test_resolve_hypothesis_rejects_invalid_transition() -> None:
    engine, _, _ = make_engine()

    investigation = engine.create(
        investigation_id=InvestigationId("inv_resolve_invalid_transition"),
        trigger="service_alert",
        objective="Determine why the service is unavailable.",
    )

    engine.collect_evidence(
        investigation_id=investigation.id,
        target="service:nginx",
        collection_method="environment.collect",
    )
    hypotheses = engine.generate_hypotheses(investigation.id)

    try:
        engine.resolve_hypothesis(
            investigation_id=investigation.id,
            hypothesis_id=hypotheses[0].id,
            target_status="supported",
        )
    except ValueError as exc:
        assert str(exc) == "Invalid hypothesis transition: proposed -> supported"
    else:
        raise AssertionError("Expected ValueError")
