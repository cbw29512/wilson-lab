# Wilson Lab Case Study

## Executive summary

Wilson Lab is a security-conscious infrastructure control-plane showcase. It combines a public React dashboard, a FastAPI API, narrow Docker operations, durable audit evidence, hardened cloud deployment, Oracle infrastructure as code, and automated verification.

The project demonstrates how I approach customer-facing technical work: understand the operational problem, reduce risk into explicit controls, build an understandable user experience, automate repeatable deployment, and prove the result with evidence.

## The problem

Infrastructure dashboards are easy to mock and dangerous to overstate. A credible control plane must answer harder questions:

- Is the displayed inventory live or demonstration data?
- Who is allowed to view or change resources?
- Which actions can the API perform?
- How are destructive or accidental actions prevented?
- Can the system prove what happened afterward?
- Can the deployment be repeated without undocumented console work?
- Does the public demonstration remain useful when the private API is unavailable?

## Constraints

- The public portfolio must never contain credentials.
- The dashboard must remain usable before a cloud account is activated.
- Docker daemon access must be isolated to a disposable showcase VM.
- The API must not expose arbitrary shell commands or general Docker access.
- Viewer and Administrator permissions must be enforced by the server.
- State-changing actions must require explicit confirmation.
- Successful and failed operations must leave durable audit evidence.
- Cloud deployment and verification must be repeatable and PowerShell-friendly.
- External blockers such as account verification and DNS ownership must remain honestly labeled.

## Solution

### Product experience

The React 19 and TypeScript dashboard provides searchable inventory, filters, sorting, resource details, role-aware actions, live-versus-demo state, and a safe fallback when the API is unavailable.

### Secure control plane

The FastAPI backend provides:

- Viewer and Administrator roles
- signed JWT sessions
- Argon2 password hashing
- failed-login throttling
- explicit-confirmation operations
- validated resource state transitions
- request IDs and no-store responses
- separate liveness and readiness checks
- persistent action requests and audit events

### Narrow Docker boundary

The Docker adapter discovers only containers labeled:

```text
wilson-lab.managed=true
```

The label is checked again immediately before an operation. The API accepts only `start`, `stop`, and `restart`. It does not expose shell execution, container creation, deletion, image pulling, arbitrary Docker commands, or host filesystem operations.

### Deployment and infrastructure

The portable deployment layer uses Docker Compose and Caddy for automatic HTTPS, file-backed secrets, non-root services, resource limits, internal demonstration networks, backup, restore, and preflight checks.

The OCI Terraform layer provisions the VCN, public subnet, routing, restricted firewall, Ubuntu ARM image, A1 Flex instance, public IP, and cloud-init bootstrap. Oracle Resource Manager can own Terraform state while the application deployment remains provider-neutral.

### Verification and evidence

The live verifier supports three levels:

1. `health` verifies HTTPS health and the exact CORS origin.
2. `read-only` verifies authentication, identity, inventory, resource details, Viewer restrictions, confirmation enforcement, and Administrator audit access.
3. `full` performs one confirmed managed operation and verifies the matching audit event.

Verification creates sanitized JSON and recruiter-readable Markdown. Tests reject passwords, bearer tokens, JWT-shaped values, and sensitive keys from evidence.

## Key engineering decisions

| Decision | Reason | Tradeoff |
|---|---|---|
| Public demo fallback | Keeps the portfolio useful during API downtime or before cloud activation | Visitors must be shown clear data provenance |
| Server-side roles | Browser controls cannot provide authorization | Requires authenticated API state |
| Label-restricted Docker adapter | Narrows a highly privileged integration | Labels are one control, not a substitute for VM isolation |
| Explicit confirmation | Prevents accidental state changes | Adds one deliberate user step |
| SQLite for the showcase | Simple, durable, and appropriate for one instance | Not a horizontally scaled production database |
| In-memory login limiter | Fits the documented single-process deployment | A scaled service would need a shared store or edge limiter |
| Separate OCI and Compose layers | Keeps deployment portable and provisioning reviewable | Two layers must remain version-compatible |
| Sanitized evidence bundle | Proves behavior without leaking credentials | Reports intentionally omit sensitive raw request data |

## Security controls

- Strong file-backed production secrets
- Production startup validation
- Viewer/Admin RBAC
- Failed-login throttling and `Retry-After`
- Explicit operation confirmation
- State-transition validation
- Docker label allowlist
- Durable success/failure auditing
- Non-root API image
- Read-only filesystems and dropped Linux capabilities
- Internal-only demonstration network
- Caddy HTTPS and security headers
- SSH restricted to one administrator `/32`
- Dependency audits for Python and production JavaScript packages
- Credential-redaction regression tests
- Private vulnerability-reporting guidance

## Verification evidence

The `0.8.0` release-preparation gates validate:

- frontend contract tests
- strict TypeScript compilation
- production Vite build
- backend Python compilation
- full backend test suite
- Compose model validation
- Caddy configuration validation
- hardened API image build
- non-root image identity
- backend dependency audit
- production frontend dependency audit

At the time of release preparation, the dependency audit reported zero known vulnerabilities across the audited backend requirements and production frontend dependency tree.

## Business and customer value

Wilson Lab is not just a collection of frameworks. It shows the ability to:

- translate infrastructure risk into understandable product behavior
- explain technical tradeoffs without hiding limitations
- separate public experience from privileged control-plane responsibilities
- design access controls around actual user roles
- automate cloud provisioning and operational verification
- produce evidence that technical and nontechnical stakeholders can review
- preserve a useful customer experience during service degradation

These are directly relevant to Sales Engineer, Solutions Consultant, Technical Account Manager, implementation, and customer-facing infrastructure roles.

## Current status

Complete in code and CI:

- dashboard
- API and role model
- safe operations and audit evidence
- deployment bundle
- OCI Terraform
- verification tooling
- recruiter evidence
- API and repository hardening

External activation remaining:

- sign in to or activate the OCI account
- apply the Resource Manager stack
- create the DNS record
- configure GitHub secrets and `VITE_API_ORIGIN`
- run live verification
- capture verified-live screenshots and recording

## Interview walkthrough

A concise demonstration should show:

1. the dashboard and clear demo/live state
2. Viewer access and unavailable controls
3. Administrator confirmation before an operation
4. the resulting audit event
5. the Terraform and deployment layers
6. the sanitized proof bundle
7. the explicit external activation boundary

Use [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) for the timed talk track.
