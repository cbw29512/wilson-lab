# Security Policy

Wilson Lab is a public security-focused showcase. Please do not use public issues, pull requests, screenshots, or recordings to disclose a vulnerability that could expose credentials, cloud identifiers, deployment details, or unintended infrastructure access.

## Supported version

Security fixes are applied to the current `main` branch. The project does not currently maintain parallel supported release branches.

## Reporting a vulnerability

Use one of these private channels:

1. Open a private GitHub security advisory for this repository when that option is available.
2. Email `divclass01@gmail.com` with the subject `Wilson Lab security report`.

Include:

- the affected component and version or commit
- clear reproduction steps
- the expected and observed behavior
- the potential impact
- any suggested mitigation

Do not include real passwords, private keys, JWTs, Oracle tenancy identifiers, Terraform state, or unrelated personal or employer infrastructure details.

## Response expectations

A report will be acknowledged as soon as reasonably possible. Valid reports will be investigated, prioritized by impact, fixed on a private branch when necessary, and disclosed publicly only after a safe remediation is available.

## Scope

In scope:

- authentication and authorization bypasses
- access to unlabeled Docker resources
- arbitrary command or Docker API exposure
- audit tampering or missing operation evidence
- credential leakage through the dashboard, API, logs, workflows, or proof bundles
- unsafe OCI, Caddy, Compose, or Terraform defaults

Out of scope:

- attacks against GitHub, Oracle Cloud, Docker, Caddy, or other third-party services themselves
- denial-of-service testing against a live demonstration instance
- social engineering, phishing, or physical attacks
- findings that require access to unrelated home, employer, or production infrastructure
- automated scans that provide no reproducible security impact

## Safety boundary

The Docker-backed runtime must remain on a disposable, dedicated sandbox. Never connect Wilson Lab to a home server, workstation, employer environment, production host, or Docker daemon containing unrelated workloads.
