# Contributing to M3D

Thank you for your interest in contributing to M3D.

M3D is an open-source runtime for safe, autonomous AI operations. The project is designed around a strict separation between operational truth, reasoning, authorization, execution, verification, and auditability.

Contributions should preserve these architectural boundaries.

## Development Setup

M3D currently targets Python 3.13+.

Create or activate a development environment, then install the project in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite with:

```bash
pytest
```

Run static checks with:

```bash
ruff check .
mypy src
```

All three checks should pass before submitting a pull request.

## Architecture

M3D uses a ports-and-adapters architecture:

```text
Domain
  ↓
Ports
  ↓
Engines
  ↓
Adapters
  ↓
Operational Environments
```

Orchestration coordinates complete operational workflows without moving infrastructure-specific concerns into the domain.

The core architectural responsibilities are:

- **Domain** — operational models, state, invariants, and transitions.
- **Ports** — contracts between the core and external capabilities.
- **Engines** — investigation, policy, risk, action, verification, and audit behavior.
- **Adapters** — implementations for environments, storage, event buses, and reasoning providers.
- **Orchestration** — coordination of multi-stage operational workflows.
- **Interfaces** — CLI and future external interfaces.

If a feature can be implemented without changing the domain model, prefer extending a port, engine, or adapter instead of modifying the domain.

## AI and Operational Truth

AI reasoning must not become the source of operational truth.

M3D separates:

- AI reasoning from domain state
- hypotheses from evidence
- decisions from authorization
- actions from execution results
- execution results from verification
- operational activity from audit history

Contributions should preserve these boundaries.

AI providers may propose hypotheses, investigation steps, conclusions, or decisions, but they must not bypass policy, authorization, verification, or audit controls.

## Adding an Environment Adapter

Environment integrations should implement the appropriate environment port rather than introducing environment-specific logic into the domain.

An environment adapter should provide capabilities such as:

- identifying the environment
- discovering entities
- observing events
- collecting information
- executing authorized operations
- verifying operational outcomes

Environment-specific implementation details belong inside the adapter.

Where possible, entity identity should remain stable across repeated discovery operations.

## Adding a Port

Ports define contracts used by the core.

A new port should:

1. Represent a meaningful capability boundary.
2. Avoid infrastructure-specific implementation details.
3. Use domain models or explicit contracts.
4. Be independently testable.
5. Have at least one adapter or a clear planned implementation.

Do not add ports simply to wrap internal functions without establishing a meaningful architectural boundary.

## Adding an Engine

Engines implement operational behavior using domain models and ports.

An engine should:

- validate its inputs
- preserve domain invariants
- avoid direct dependencies on concrete infrastructure adapters
- persist state through defined ports where appropriate
- produce explicit results
- make failure conditions observable

Engines should not silently bypass policy, authorization, verification, or audit requirements.

## Actions and Safety

Operational actions are deliberately separated into stages.

The normal lifecycle is:

```text
PROPOSED
   ↓
AUTHORIZED
   ↓
EXECUTING
   ↓
COMPLETED
```

Alternative outcomes include failure, rejection, cancellation, or rollback.

An action should not be considered operationally successful merely because a command returned successfully.

Verification must establish whether the intended operational outcome actually occurred.

Contributions that introduce new execution capabilities should include appropriate authorization and verification behavior.

## Policy and Authorization

Policy evaluation and authorization are separate concepts.

Policy determines whether an action is:

- allowed
- denied
- requires approval

Authorization determines whether a specific action has actually been permitted to execute.

AI reasoning must not override a policy decision or manufacture authorization.

## Testing

New functionality should include tests appropriate to its scope.

Use:

- `tests/unit/` for isolated domain and engine behavior
- `tests/integration/` for adapter and infrastructure integration
- `tests/scenarios/` for complete operational workflows
- `tests/benchmarks/` for performance or evaluation work

When fixing a bug, add a regression test whenever practical.

Environment-specific tests should avoid assumptions that only hold on the contributor's machine.

Tests involving real infrastructure should be clearly separated from deterministic unit tests.

## Code Quality

M3D uses:

- Ruff for linting
- mypy for static type checking
- pytest for testing

Before submitting a pull request, run:

```bash
pytest
ruff check .
mypy src
```

Keep changes focused and avoid unrelated formatting or refactoring.

## Pull Requests

A pull request should clearly explain:

- what changed
- why the change is needed
- which architectural layer was affected
- how the change was tested
- whether any new permissions or operational capabilities were introduced

Keep pull requests focused on a coherent change.

Large architectural changes should be discussed before implementation when possible.

## Commit Messages

Use concise commit messages that describe the change.

Examples:

```text
Add Docker environment adapter
Add action verification engine
Fix stable entity identity
Add policy evaluation tests
```

Avoid vague messages such as:

```text
Update stuff
Changes
Fix things
```

## Documentation

Changes to public behavior or architecture should include corresponding documentation updates.

If a new capability changes how users interact with M3D, update the README or relevant documentation.

Architectural changes should preserve the terminology used throughout the project.

## Security

Do not commit:

- API keys
- passwords
- access tokens
- private certificates
- private SSH keys
- credentials
- personal machine secrets
- production configuration containing sensitive information

Security vulnerabilities should be reported according to `SECURITY.md` rather than disclosed publicly in an issue.

## Good First Contributions

Useful early contributions include:

- additional environment adapters
- additional storage adapters
- event bus adapters
- reasoning provider adapters
- domain and engine tests
- documentation improvements
- examples
- benchmark scenarios
- developer tooling
- observability integrations

Contributions should strengthen the runtime and its architectural boundaries rather than turning M3D into a generic chatbot or agent framework.

## Design Principle

The central principle for contributors is:

> **AI may reason about the environment, but M3D owns state, evidence, policy, execution, verification, and audit.**

When in doubt, preserve that separation.
