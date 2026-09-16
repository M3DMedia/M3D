"""Core orchestration engine for operational investigations."""

from __future__ import annotations

from dataclasses import replace

from m3d.domain.common.types import (
    DecisionId,
    EntityId,
    EnvironmentId,
    EvidenceId,
    HypothesisId,
    InvestigationId,
    new_id,
)
from m3d.domain.decision import Decision
from m3d.domain.event import Event
from m3d.domain.evidence import Evidence
from m3d.domain.hypothesis import Hypothesis
from m3d.domain.investigation import Investigation
from m3d.domain.risk import Risk
from m3d.ports.environment import EnvironmentPlugin
from m3d.ports.event_bus import EventBus
from m3d.ports.investigation import InvestigationStore
from m3d.ports.reasoning import ReasoningProvider
from m3d.ports.risk import RiskEngine


class InvestigationEngine:
    """Coordinate the lifecycle of operational investigations."""

    def __init__(
        self,
        store: InvestigationStore,
        environment: EnvironmentPlugin,
        event_bus: EventBus,
        reasoning: ReasoningProvider,
        risk_engine: RiskEngine,
    ) -> None:
        self._store = store
        self._environment = environment
        self._event_bus = event_bus
        self._reasoning = reasoning
        self._risk_engine = risk_engine

    def create(
        self,
        investigation_id: InvestigationId,
        trigger: str,
        objective: str,
    ) -> Investigation:
        """Create and persist a new investigation."""
        investigation = Investigation(
            id=investigation_id,
            environment_id=EnvironmentId(self._environment.identify()),
            trigger=trigger,
            objective=objective,
        )
        self._store.save_investigation(investigation)
        return investigation

    def get(self, investigation_id: InvestigationId) -> Investigation | None:
        """Retrieve an investigation by identifier."""
        return self._store.get_investigation(str(investigation_id))

    def get_hypothesis(self, hypothesis_id: HypothesisId) -> Hypothesis | None:
        """Retrieve a persisted hypothesis by identifier."""
        return self._store.get_hypothesis(str(hypothesis_id))

    def scope(
        self,
        investigation_id: InvestigationId,
        scope: tuple[str, ...],
    ) -> Investigation:
        """Define the investigation scope and persist the updated investigation."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")

        if not scope:
            raise ValueError("Investigation scope cannot be empty.")

        scoped = investigation.transition_to(
            "scoping",
            scope=scope,
        )
        self._store.save_investigation(scoped)
        return scoped

    def start_collection(
        self,
        investigation_id: InvestigationId,
    ) -> Investigation:
        """Transition a scoped investigation into evidence collection."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")

        collecting = investigation.transition_to("collecting")
        self._store.save_investigation(collecting)
        return collecting

    def start_analysis(
        self,
        investigation_id: InvestigationId,
    ) -> Investigation:
        """Transition a collecting investigation into analysis."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")

        analyzing = investigation.transition_to("analyzing")
        self._store.save_investigation(analyzing)
        return analyzing

    def start_hypothesis_generation(
        self,
        investigation_id: InvestigationId,
    ) -> Investigation:
        """Transition an analyzing investigation into hypothesis generation."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")

        hypothesis = investigation.transition_to("hypothesis")
        self._store.save_investigation(hypothesis)
        return hypothesis

    def evaluate_hypothesis(
        self,
        investigation_id: InvestigationId,
        hypothesis_id: HypothesisId,
) -> float:
        """Evaluate a persisted hypothesis against investigation evidence."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")
        if investigation.status != "testing":
            raise ValueError("Investigation must be in testing state.")

        hypothesis = self._store.get_hypothesis(str(hypothesis_id))
        if hypothesis is None:
            raise ValueError(f"Hypothesis not found: {hypothesis_id}")
        if hypothesis.investigation_id != investigation.id:
            raise ValueError(
                "Hypothesis does not belong to the requested investigation."
            )
        evidence = self._store.get_evidence(str(investigation_id))
        return self._reasoning.evaluate_evidence(
            investigation,
            hypothesis,
            evidence,
        )

    def evaluate_result(
        self,
        investigation_id: InvestigationId,
        hypothesis_id: HypothesisId,
    ) -> str:
        """Evaluate the collected result against a persisted hypothesis."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")
        if investigation.status != "testing":
            raise ValueError("Investigation must be in testing state.")
        hypothesis = self._store.get_hypothesis(str(hypothesis_id))
        if hypothesis is None:
            raise ValueError(f"Hypothesis not found: {hypothesis_id}")
        if hypothesis.investigation_id != investigation.id:
            raise ValueError(
                "Hypothesis does not belong to the requested investigation."
            )
        evidence = self._store.get_evidence(str(investigation_id))
        return self._reasoning.evaluate_result(
            investigation,
            hypothesis,
            evidence,
        )

    def resolve_hypothesis(
        self,
        investigation_id: InvestigationId,
        hypothesis_id: HypothesisId,
        target_status: str,
    ) -> Hypothesis:
        """Transition and persist a hypothesis to its requested state."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")

        hypothesis = self._store.get_hypothesis(str(hypothesis_id))
        if hypothesis is None:
            raise ValueError(f"Hypothesis not found: {hypothesis_id}")
        if hypothesis.investigation_id != investigation.id:
            raise ValueError(
                "Hypothesis does not belong to the requested investigation."
            )

        resolved = hypothesis.transition_to(target_status)
        self._store.save_hypothesis(resolved)
        return resolved

    def start_testing(
        self,
        investigation_id: InvestigationId,
    ) -> Investigation:
        """Transition a hypothesis-stage investigation into testing."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")

        testing = investigation.transition_to("testing")
        self._store.save_investigation(testing)
        return testing

    def start_conclusion(
        self,
        investigation_id: InvestigationId,
    ) -> Investigation:
        """Transition a testing investigation into the conclusion stage."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")

        conclusion = investigation.transition_to("conclusion")
        self._store.save_investigation(conclusion)
        return conclusion

    def generate_conclusion(
        self,
        investigation_id: InvestigationId,
    ) -> Investigation:
        """Generate and persist the investigation conclusion."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")
        if investigation.status != "conclusion":
            raise ValueError("Investigation must be in conclusion state.")

        evidence = self._store.get_evidence(str(investigation_id))
        hypotheses = self._store.get_hypotheses(str(investigation_id))
        conclusion = self._reasoning.generate_conclusion(
            investigation,
            evidence,
            hypotheses,
        )
        if not conclusion.strip():
            raise ValueError("Investigation conclusion cannot be empty.")

        concluded = replace(
            investigation,
            conclusion=conclusion,
        )
        self._store.save_investigation(concluded)
        return concluded

    def propose_decision(
        self,
        investigation_id: InvestigationId,
        decision: str,
        rationale: str,
        confidence: float = 0.0,
    ) -> Decision:
        """Create and persist a proposed decision for an investigation."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")
        if investigation.status != "completed":
            raise ValueError("Investigation must be completed before proposing a decision.")
        if not investigation.conclusion or not investigation.conclusion.strip():
            raise ValueError("Investigation conclusion is required before proposing a decision.")
        if not decision.strip():
            raise ValueError("Decision cannot be empty.")
        if not rationale.strip():
            raise ValueError("Decision rationale cannot be empty.")

        evidence = self._store.get_evidence(str(investigation_id))
        decision_record = Decision(
            id=DecisionId(new_id("decision")),
            investigation_id=investigation.id,
            decision=decision,
            rationale=rationale,
            evidence_ids=tuple(item.id for item in evidence),
            confidence=confidence,
        )
        self._store.save_decision(decision_record)
        return decision_record

    def assess_decision_risk(
        self,
        decision_id: DecisionId,
    ) -> Risk:
        """Assess and persist the risk associated with a decision."""
        decision = self._store.get_decision(str(decision_id))
        if decision is None:
            raise ValueError(f"Decision not found: {decision_id}")
        risk = self._risk_engine.assess(decision)
        self._store.save_risk(risk)
        return risk

    def complete(
        self,
        investigation_id: InvestigationId,
    ) -> Investigation:
        """Transition a conclusion-stage investigation into completed."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")

        completed = investigation.transition_to("completed")
        if not investigation.conclusion or not investigation.conclusion.strip():
            raise ValueError("Investigation conclusion is required before completion.")
        self._store.save_investigation(completed)
        return completed

    def subscribe_to_event(
        self,
        event_type: str,
        objective: str,
    ) -> None:
        """Create an investigation whenever a subscribed event is published."""
        if not event_type.strip():
            raise ValueError("Event type cannot be empty.")

        if not objective.strip():
            raise ValueError("Investigation objective cannot be empty.")

        def handle_event(event: Event) -> None:
            self.create(
                investigation_id=InvestigationId(new_id("inv")),
                trigger=event.type,
                objective=objective,
            )

        self._event_bus.subscribe(event_type, handle_event)

    def collect_evidence(
        self,
        investigation_id: InvestigationId,
        target: str,
        collection_method: str,
        entity_id: str | None = None,
    ) -> Evidence:
        """Collect information from the environment and persist it as evidence."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")

        if not target.strip():
            raise ValueError("Evidence target cannot be empty.")

        if not collection_method.strip():
            raise ValueError("Collection method cannot be empty.")

        collection_result = self._environment.collect(target)

        from datetime import UTC, datetime

        evidence = Evidence(
            id=EvidenceId(new_id("evidence")),
            investigation_id=investigation.id,
            source=self._environment.__class__.__name__,
            observation=str(collection_result),
            collected_at=datetime.now(UTC),
            collection_method=collection_method,
            entity_id=EntityId(entity_id) if entity_id is not None else None,
            metadata={"target": target, "collection_result": collection_result},
        )

        self._store.save_evidence(evidence)
        return evidence

    def generate_hypotheses(
        self,
        investigation_id: InvestigationId,
    ) -> list[Hypothesis]:
        """Generate and persist hypotheses for an investigation."""
        investigation = self._store.get_investigation(str(investigation_id))
        if investigation is None:
            raise ValueError(f"Investigation not found: {investigation_id}")

        evidence = self._store.get_evidence(str(investigation_id))
        hypotheses = self._reasoning.generate_hypotheses(
            investigation,
            evidence,
        )

        for hypothesis in hypotheses:
            if hypothesis.investigation_id != investigation.id:
                raise ValueError(
                    "Reasoning provider returned a hypothesis for another investigation."
                )
            self._store.save_hypothesis(hypothesis)

        return hypotheses
