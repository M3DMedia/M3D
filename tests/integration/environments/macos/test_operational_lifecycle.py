import pytest

from m3d.adapters.authorization.manual import ManualAuthorizationProvider
from m3d.adapters.environments.macos import MacOSEnvironmentPlugin
from m3d.adapters.storage.memory.audit_store import InMemoryAuditStore
from m3d.adapters.storage.memory.investigation_store import InMemoryInvestigationStore
from m3d.adapters.verification.environment import EnvironmentVerifier
from m3d.domain.action_result import ActionResult
from m3d.domain.authorization import Authorization
from m3d.domain.common.types import ActionId, AuthorizationId, utc_now
from m3d.domain.decision import Decision
from m3d.domain.investigation import Investigation
from m3d.domain.policy_evaluation import PolicyEvaluation
from m3d.engines.action import DefaultActionEngine
from m3d.engines.audit import DefaultAuditEngine
from m3d.engines.orchestration import OperationalOrchestrator
from m3d.engines.verification import DefaultVerificationEngine
from m3d.ports.action import ActionExecutor


class MacOSActionExecutor(ActionExecutor):
    """Execute M3D actions through the real macOS environment adapter."""

    def __init__(self, environment: MacOSEnvironmentPlugin) -> None:
        self._environment = environment

    def execute(self, action):
        parameters = action.metadata.get("parameters", {})
        if not isinstance(parameters, dict):
            raise TypeError("Action parameters must be a mapping.")

        output = self._environment.execute(action.action_type, parameters)

        return ActionResult(
            id=f"result-{action.id}",
            action_id=ActionId(action.id),
            status="succeeded",
            output=str(output),
            completed_at=utc_now(),
            metadata={
                "environment_id": str(self._environment.identify()),
                "operation": action.action_type,
            },
        )



pytestmark = pytest.mark.macos

def test_real_macos_operational_lifecycle():
    environment = MacOSEnvironmentPlugin()
    store = InMemoryInvestigationStore()
    audit_store = InMemoryAuditStore()
    audit_engine = DefaultAuditEngine(audit_store)

    authorization_provider = ManualAuthorizationProvider()
    executor = MacOSActionExecutor(environment)
    action_engine = DefaultActionEngine(authorization_provider, executor)

    verifier = EnvironmentVerifier(environment)
    verification_engine = DefaultVerificationEngine(verifier)

    orchestrator = OperationalOrchestrator(
        store=store,
        action_engine=action_engine,
        verification_engine=verification_engine,
        audit_engine=audit_engine,
    )

    host = environment.discover()[0]

    investigation = Investigation(
        id="investigation-macos-lifecycle",
        environment_id=environment.identify(),
        trigger="integration_test",
        objective="Read the local macOS hostname without modifying the environment.",
    )
    store.save_investigation(investigation)

    decision = Decision(
        id="decision-macos-lifecycle",
        investigation_id=investigation.id,
        decision="Read the local macOS hostname.",
        rationale="Integration test of the operational lifecycle.",
    )
    store.save_decision(decision)

    policy_evaluation = PolicyEvaluation(
        id="policy-evaluation-macos-lifecycle",
        decision_id=decision.id,
        policy_id="policy-test",
        status="evaluated",
        result="allowed",
        reason="Integration test action explicitly allowed.",
    )
    store.save_policy_evaluation(policy_evaluation)

    action = orchestrator.propose_action(
        decision_id=decision.id,
        action_type="get_hostname",
        description="Read the local macOS hostname.",
        requested_by="integration-test",
        metadata={
            "parameters": {},
            "verification": {
                "target": "host",
                "expected_outcome": "host_present",
            },
        },
    )

    assert action.status == "proposed"
    assert action.authorization_id is None

    authorization = orchestrator.request_authorization(action.id)
    assert authorization.status == "requested"

    granted = Authorization(
        id=AuthorizationId(authorization.id),
        action_id=ActionId(action.id),
        requested_by=authorization.requested_by,
        status="granted",
        granted_by="integration-test",
        reason="Explicit approval for harmless hostname read.",
        requested_at=authorization.requested_at,
        resolved_at=utc_now(),
        metadata=authorization.metadata,
    )
    store.save_authorization(granted)

    authorized_action = orchestrator.authorize_action(action.id, granted.id)
    assert authorized_action.status == "authorized"
    assert authorized_action.authorization_id == granted.id

    result = orchestrator.execute_action(action.id)
    assert result.status == "succeeded"
    assert result.output is not None
    assert host.name in result.output

    verification = orchestrator.verify_action(action.id)
    assert verification.status == "verified"
    assert verification.expected_outcome == "host_present"

    records = audit_engine.list_by_correlation(action.id)
    event_types = [record.event_type for record in records]

    assert "action.proposed" in event_types
