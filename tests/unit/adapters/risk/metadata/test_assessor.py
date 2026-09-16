"""Tests for the metadata risk assessor."""

import pytest

from m3d.adapters.risk.metadata import MetadataRiskAssessor
from m3d.domain.common.types import DecisionId, InvestigationId
from m3d.domain.decision import Decision


def make_decision(metadata: dict[str, object]) -> Decision:
    """Create a decision containing risk metadata."""
    return Decision(
        id=DecisionId("dec_test"),
        investigation_id=InvestigationId("inv_test"),
        decision="restart_service",
        rationale="The service is unavailable.",
        metadata=metadata,
    )


def test_assess_builds_risk_from_metadata() -> None:
    assessor = MetadataRiskAssessor()

    decision = make_decision(
        {
            "risk": {
                "severity": "high",
                "probability": 0.7,
                "impact": "Service interruption may affect dependent systems.",
                "reversibility": "partially reversible",
                "affected_entities": ["ent_test"],
                "mitigation": "Restart during the maintenance window.",
                "required_authorization": "operations_manager",
            }
        }
    )

    risk = assessor.assess(decision)

    assert risk.decision_id == decision.id
    assert risk.severity == "high"
    assert risk.probability == 0.7
    assert risk.impact == "Service interruption may affect dependent systems."
    assert risk.reversibility == "partially reversible"
    assert risk.affected_entities == ("ent_test",)
    assert risk.mitigation == "Restart during the maintenance window."
    assert risk.required_authorization == "operations_manager"
    assert risk.metadata["assessment_method"] == "metadata"


def test_assess_allows_optional_fields_to_be_omitted() -> None:
    assessor = MetadataRiskAssessor()

    decision = make_decision(
        {
            "risk": {
                "severity": "low",
                "probability": 0.2,
                "impact": "Minor service disruption.",
                "reversibility": "reversible",
            }
        }
    )

    risk = assessor.assess(decision)

    assert risk.affected_entities == ()
    assert risk.mitigation is None
    assert risk.required_authorization is None


def test_missing_risk_metadata_is_rejected() -> None:
    assessor = MetadataRiskAssessor()
    decision = make_decision({})

    with pytest.raises(TypeError, match="risk metadata must be a mapping"):
        assessor.assess(decision)


def test_missing_required_field_is_rejected() -> None:
    assessor = MetadataRiskAssessor()
    decision = make_decision(
        {
            "risk": {
                "severity": "high",
                "probability": 0.7,
                "impact": "Service interruption.",
            }
        }
    )

    with pytest.raises(ValueError, match="Missing required risk field: reversibility"):
        assessor.assess(decision)


def test_invalid_probability_type_is_rejected() -> None:
    assessor = MetadataRiskAssessor()
    decision = make_decision(
        {
            "risk": {
                "severity": "high",
                "probability": "high",
                "impact": "Service interruption.",
                "reversibility": "reversible",
            }
        }
    )

    with pytest.raises(TypeError, match="Risk probability must be numeric"):
        assessor.assess(decision)


def test_invalid_affected_entities_are_rejected() -> None:
    assessor = MetadataRiskAssessor()
    decision = make_decision(
        {
            "risk": {
                "severity": "high",
                "probability": 0.7,
                "impact": "Service interruption.",
                "reversibility": "reversible",
                "affected_entities": "ent_test",
            }
        }
    )

    with pytest.raises(TypeError, match="affected_entities must be a list or tuple"):
        assessor.assess(decision)


def test_invalid_required_string_is_rejected() -> None:
    assessor = MetadataRiskAssessor()
    decision = make_decision(
        {
            "risk": {
                "severity": "",
                "probability": 0.7,
                "impact": "Service interruption.",
                "reversibility": "reversible",
            }
        }
    )

    with pytest.raises(ValueError, match="Risk severity must be a non-empty string"):
        assessor.assess(decision)


def test_probability_range_is_validated_by_risk_model() -> None:
    assessor = MetadataRiskAssessor()
    decision = make_decision(
        {
            "risk": {
                "severity": "high",
                "probability": 1.5,
                "impact": "Service interruption.",
                "reversibility": "reversible",
            }
        }
    )

    with pytest.raises(
        ValueError,
        match="Risk probability must be between 0.0 and 1.0",
    ):
        assessor.assess(decision)
