"""Core orchestration engine for operational investigations."""

from __future__ import annotations

from m3d.domain.common.types import EntityId, EnvironmentId, EvidenceId, InvestigationId, new_id
from m3d.domain.event import Event
from m3d.domain.evidence import Evidence
from m3d.domain.hypothesis import Hypothesis
from m3d.domain.investigation import Investigation
from m3d.ports.environment import EnvironmentPlugin
from m3d.ports.event_bus import EventBus
from m3d.ports.investigation import InvestigationStore
from m3d.ports.reasoning import ReasoningProvider


class InvestigationEngine:
    """Coordinate the lifecycle of operational investigations."""

    def __init__(
        self,
        store: InvestigationStore,
        environment: EnvironmentPlugin,
        event_bus: EventBus,
        reasoning: ReasoningProvider,
    ) -> None:
        self._store = store
        self._environment = environment
        self._event_bus = event_bus
        self._reasoning = reasoning

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
