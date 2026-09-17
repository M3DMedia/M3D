# Security Policy

## Overview

M3D is an open-source runtime for safe, autonomous AI operations.

Security is a core architectural concern of the project. M3D is designed to separate AI reasoning from operational authority, execution, verification, and auditability.

Security reports are especially important when they could allow an attacker or unauthorized component to:

- bypass policy controls
- bypass authorization requirements
- execute an operational action without appropriate permission
- alter or forge operational state
- suppress or manipulate verification
- tamper with audit history
- expose credentials or sensitive operational information
- compromise an environment through an M3D component
- cause an AI reasoning component to gain unintended operational authority

## Supported Versions

Security fixes are generally focused on the latest released version and the current development branch.

| Version | Supported |
| --- | --- |
| Latest release | Yes |
| Development branch | Yes |
| Older releases | Limited |

Users should keep M3D updated to the latest available release whenever possible.

## Reporting a Vulnerability

Please do not disclose security vulnerabilities publicly through GitHub Issues, pull requests, discussions, or other public channels.

For a vulnerability that could affect M3D users or operational environments, use GitHub's private vulnerability reporting mechanism when it is enabled for the repository.

If private vulnerability reporting is not yet available, contact the project maintainers through a private communication channel associated with the M3D project.

When reporting a vulnerability, include as much of the following information as possible:

- a clear description of the vulnerability
- the affected M3D version or commit
- the affected component or architectural layer
- steps required to reproduce the issue
- a minimal proof of concept when appropriate
- expected behavior
- actual behavior
- potential security impact
- relevant logs or error messages
- whether exploitation requires special permissions or configuration
- whether the issue affects confidentiality, integrity, availability, authorization, or operational safety

Please avoid including real credentials, private keys, production secrets, or sensitive personal information in a report.

## What Should Be Reported

Examples of security issues include, but are not limited to:

### Policy and Authorization Bypass

Report vulnerabilities that allow an action to execute despite:

- a denied policy evaluation
- a required approval that was not granted
- an invalid or expired authorization
- an authorization belonging to another action
- missing authorization

### Action Execution

Report vulnerabilities that allow unauthorized operational execution or allow an action to bypass the normal action lifecycle.

The expected lifecycle is:

```text
PROPOSED
   ↓
AUTHORIZED
   ↓
EXECUTING
   ↓
COMPLETED
```

Unexpected transitions, authorization confusion, or execution paths that circumvent these controls may represent security vulnerabilities.

### Verification Bypass

M3D treats successful command execution and successful operational outcomes as separate concepts.

Report vulnerabilities that allow an action to be considered verified without appropriate verification evidence, or that allow verification results to be forged, suppressed, or incorrectly associated with another action.

### Audit Integrity

M3D uses audit records to preserve operational history and accountability.

Report vulnerabilities that allow unauthorized modification, deletion, substitution, or falsification of audit records.

### Environment Adapters

Environment adapters connect M3D to operational systems.

Report vulnerabilities where an adapter can:

- execute unintended commands
- bypass authorization
- expose sensitive environment information
- confuse entity identity
- operate on the wrong environment or entity
- incorrectly report execution or verification results

### AI Reasoning Boundaries

AI providers are intended to provide reasoning capabilities, not operational authority.

Report vulnerabilities where untrusted or manipulated AI output can directly bypass M3D controls or cause unauthorized operational actions.

Examples include prompt-driven policy bypasses, unsafe tool escalation, or paths where model output is treated as trusted authority without appropriate validation.

## Secrets and Credentials

Never commit secrets to the repository.

This includes:

- API keys
- passwords
- access tokens
- private SSH keys
- private certificates
- cloud credentials
- database credentials
- production configuration containing secrets
- environment files containing sensitive values

If a secret is accidentally committed:

1. Treat the secret as compromised.
2. Revoke or rotate it immediately.
3. Remove it from the repository history where appropriate.
4. Notify the relevant service or system owner.
5. Report the incident privately if it creates a security risk for M3D users.

Removing a secret from the latest commit does not necessarily remove it from Git history.

## Operational Safety

M3D can eventually interact with real operational environments. Security therefore includes operational safety.

Contributors should not introduce execution paths that:

- silently perform privileged operations
- weaken policy enforcement
- automatically grant authorization
- skip verification
- conceal operational failures
- modify audit history
- treat model output as authorization
- make destructive operations irreversible without appropriate controls

New operational capabilities should have appropriate tests covering authorization, execution, failure handling, and verification.

## Responsible Disclosure

Please allow maintainers reasonable time to investigate and address a privately reported vulnerability before making technical details public.

Security fixes may require:

- code changes
- regression tests
- documentation changes
- release notes
- dependency updates
- configuration changes
- coordinated disclosure

The project may publish a security advisory when appropriate.

## Security Research

Good-faith security research is welcome.

Researchers should:

- avoid accessing data that does not belong to them
- avoid disrupting systems or services
- avoid destructive testing against production environments
- avoid exposing credentials or private information
- stop testing if sensitive information is unintentionally accessed
- report findings privately when they present a meaningful security risk

Testing should be performed against systems and environments for which the researcher has authorization.

## Dependency Security

Dependencies should be kept current where practical.

Security-sensitive dependency updates should be reviewed for compatibility and regression risk before being merged.

Contributors should avoid adding dependencies without a clear technical reason, especially when the dependency introduces privileged system access, network access, credential handling, or code execution.

## Security Design Principle

M3D follows a simple security principle:

> **AI may reason about the environment, but M3D owns state, evidence, policy, execution, verification, and audit.**

Security-sensitive contributions should preserve this separation of responsibilities.

## Contact

Security reports should be submitted privately through the project's configured GitHub security reporting mechanism once enabled.

For the current development phase, consult the repository maintainers for the appropriate private reporting channel.
