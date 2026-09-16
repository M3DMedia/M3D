"""Deterministic risk assessor using decision metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from m3d.domain.common.types import RiskId, new_id
from m3d.domain.decision import Decision
from m3d.domain.risk import Risk
from m3d.ports.risk_assessor import RiskAssessor


class MetadataRiskAssessor(RiskAssessor):
    """Build a risk assessment from explicitly supplied decision metadata."""

    REQUIRED_FIELDS = (
        "severity",
        "probability",
        "impact",
        "reversibility",
    )

    def assess(self, decision: Decision) -> Risk:
        """Create a risk from the decision's risk metadata."""
        raw_risk = decision.metadata.get("risk")

        if not isinstance(raw_risk, Mapping):
            raise TypeError("Decision risk metadata must be a mapping.")

        for field in self.REQUIRED_FIELDS:
            if field not in raw_risk:
                raise ValueError(f"Missing required risk field: {field}")

        probability = raw_risk["probability"]

        if isinstance(probability, bool) or not isinstance(probability, (int, float)):
            raise TypeError("Risk probability must be numeric.")

        affected_entities = self._parse_entities(raw_risk.get("affected_entities", ()))

        mitigation = self._parse_optional_string(raw_risk.get("mitigation"))
        required_authorization = self._parse_optional_string(raw_risk.get("required_authorization"))

        return Risk(
            id=RiskId(new_id("risk")),
            decision_id=decision.id,
            severity=self._required_string(raw_risk["severity"], "severity"),
            probability=float(probability),
            impact=self._required_string(raw_risk["impact"], "impact"),
            reversibility=self._required_string(
                raw_risk["reversibility"],
                "reversibility",
            ),
            affected_entities=affected_entities,
            mitigation=mitigation,
            required_authorization=required_authorization,
            metadata={
                "assessment_method": "metadata",
            },
        )

    def _required_string(self, value: Any, field: str) -> str:
        """Validate and return a required string field."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Risk {field} must be a non-empty string.")
        return value

    def _parse_entities(self, value: Any) -> tuple[str, ...]:
        """Validate and return affected entity identifiers."""
        if value is None:
            return ()

        if isinstance(value, str) or not isinstance(value, (list, tuple)):
            raise TypeError("Risk affected_entities must be a list or tuple.")

        entities: list[str] = []

        for entity in value:
            if not isinstance(entity, str) or not entity.strip():
                raise ValueError("Risk affected_entities must contain non-empty strings.")
            entities.append(entity)

        return tuple(entities)

    def _parse_optional_string(self, value: Any) -> str | None:
        """Validate an optional string field."""
        if value is None:
            return None

        if not isinstance(value, str) or not value.strip():
            raise ValueError("Optional risk fields must be non-empty strings.")

        return value
