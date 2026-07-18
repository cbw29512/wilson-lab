# Wilson Lab Interview Demo

## Objective

Demonstrate product judgment, customer communication, security boundaries, software delivery, infrastructure automation, and operational evidence in approximately three minutes.

The demonstration should answer four questions:

1. What customer problem does Wilson Lab solve?
2. What can each user safely do?
3. Why is the control plane safer than direct Docker access?
4. What evidence proves the live system behaves as described?

## Preparation

Before presenting:

- Open the public dashboard in a clean browser window.
- Confirm the dashboard identifies whether it is using Demo Data or Live Inventory.
- Keep Viewer and Administrator credentials in a password manager, not in notes or browser bookmarks.
- Run `Live Deployment Verification` at `read-only` level.
- Run `full` verification once after deployment changes.
- Download the resulting JSON and Markdown proof bundle.
- Open the latest successful frontend, backend, deployment, infrastructure, and verification workflow results.
- Never display Oracle tenancy identifiers, passwords, bearer tokens, SSH keys, Terraform state, or generated secret files.

## Three-minute demonstration

### 0:00–0:30 — Frame the customer problem

Say:

> Small technical teams often need to understand and operate lab infrastructure, but giving every user direct Docker or host access creates unnecessary risk. Wilson Lab provides a deliberately narrow control plane around inventory, roles, confirmation, and auditability.

Explain that this is not a general Docker administrator. It is a product demonstration of how to expose a small set of useful operations while preserving clear security boundaries.

### 0:30–1:00 — Show the public product surface

Open the GitHub Pages dashboard.

Point out:

- API availability
- Demo Data versus Live Inventory
- search
- tag filtering
- status and environment indicators
- UTC update times
- resource detail drawer

Say:

> The public site remains useful even when the API is unavailable. It never presents simulated data as live data, and an expired or invalid session returns safely to demo mode.

This demonstrates resilience and honest data provenance rather than hiding an outage behind stale information.

### 1:00–1:35 — Demonstrate Viewer access

Sign in as Viewer.

Show:

- identity and role
- validated live inventory
- resource details
- absence of state-changing controls

Say:

> Hiding buttons is only a usability feature. The server remains authoritative. The verification suite directly calls the operation and audit endpoints with a Viewer token and confirms both return HTTP 403.

Do not expose the token or password.

### 1:35–2:20 — Demonstrate Administrator controls

Sign out and sign in as Administrator.

1. Open a running managed resource.
2. Select `restart` when available.
3. Show the explicit confirmation dialog.
4. Explain that an unconfirmed API request receives HTTP 409.
5. Confirm the operation.
6. Show the updated resource.
7. Open the audit timeline.
8. Identify the actor, resource, outcome, timestamp, and action-request identifier.

Say:

> The browser sends a structured enum, not a Docker command. The API validates the role, confirmation, current state, and management label before the runtime adapter performs the transition. The resulting request identifier links the operation response to durable audit evidence.

### 2:20–2:45 — Show infrastructure and delivery evidence

Briefly show the repository architecture or README diagram.

Explain:

- React and TypeScript frontend on GitHub Pages
- Caddy automatic HTTPS
- FastAPI authorization boundary
- SQLite audit persistence
- label-restricted Docker runtime
- internal demo containers with no host ports
- Terraform-managed OCI VCN, firewall, and Ubuntu A1 VM
- cloud-init bootstrap

Then show the successful workflow categories:

- frontend
- backend
- deployment
- infrastructure
- verification tooling

### 2:45–3:00 — Close with proof

Open the generated Markdown evidence summary.

Say:

> This proof bundle is generated from the live verifier. It checks HTTPS, exact CORS, identity, Viewer restrictions, confirmation, managed operations, and matching audit events. A second renderer rejects credential-like fields and JWT-shaped values before producing recruiter-readable evidence.

Close with:

> Wilson Lab shows how I move from a broad customer need to a working product, define a narrow security model, automate deployment, and produce evidence that the system behaves as claimed.

## Safety controls to mention when asked

- The browser contains no credentials.
- Session tokens use session-scoped browser storage.
- Viewer and Administrator decisions are enforced by the API.
- Every state-changing request requires explicit confirmation.
- Only `start`, `stop`, and `restart` enums are accepted.
- Allowed actions derive from current resource state.
- Docker discovery is filtered to `wilson-lab.managed=true`.
- The management label is checked again before an operation.
- No shell, create, delete, pull, host-path, or arbitrary Docker API is exposed.
- Demo containers publish no public host ports.
- Caddy is the only public application entry point.
- SSH is limited to one administrator `/32` in OCI.
- The Docker-backed deployment is isolated from home, employer, and production systems.
- Scheduled verification is health-only and cannot change state.
- Full verification must be manually triggered.
- JSON and Markdown evidence exclude passwords and bearer tokens.

## Evidence fallback when the API is unavailable

Do not pretend the API is live.

1. Point out the dashboard's unavailable and Demo Data indicators.
2. Explain the deliberate fallback behavior.
3. Show the most recent successful sanitized proof bundle.
4. Show the relevant failed health workflow when the outage is current.
5. Explain the investigation path through Caddy, API, cloud-init, and Docker logs.

Say:

> The public experience degrades safely and visibly. The dashboard stays usable, but it clearly distinguishes demo data from current live inventory.

## Truthful status language

### Before OCI and DNS activation

Use:

> The complete application, deployment bundle, Oracle infrastructure code, and live verification tooling are implemented and validated in CI. Public API activation requires the external OCI account and DNS step.

Do not say that the API is publicly live.

### After health verification passes

Use:

> The isolated HTTPS API is deployed and its production Docker health contract is passing.

### After read-only verification passes

Use:

> Viewer and Administrator identity, inventory, RBAC, confirmation enforcement, and audit access have been verified against the live API.

### After full verification passes

Use:

> A confirmed managed operation completed successfully and was linked to a matching live audit event through the action-request identifier.

## Common interview questions

### Why not give users direct Docker access?

Direct daemon access is effectively host-level administrative access. Wilson Lab replaces that broad interface with a small product surface, server-side roles, structured actions, state validation, labels, confirmation, and audit evidence.

### Why use SQLite?

The showcase is a single-instance deployment. SQLite keeps the demonstration understandable and portable. A production multi-instance service would use managed persistence, schema migrations, centralized audit storage, and stronger availability guarantees.

### Why keep Demo Data fallback?

A portfolio should remain useful during backend downtime, but it must never misrepresent simulated information as live. The source indicator makes that boundary explicit.

### Why Oracle Terraform and a separate Compose layer?

Terraform manages provider-specific network and compute resources. Compose manages the portable application stack. Separating them keeps the deployment reusable while preserving repeatable OCI provisioning.

### Why generate a proof bundle?

Screenshots show appearance, not control behavior. The verifier exercises the API contract, and the renderer converts sanitized results into evidence an interviewer can understand without revealing credentials.

### What would change for production?

Use managed identity, short-lived sessions, centralized rate limiting, managed secrets, a production database, migrations, append-only external audit storage, stronger observability, policy enforcement outside the web process, and a Docker alternative with a narrower privilege boundary.

## Final recording checklist

- Dashboard source indicator is visible.
- No passwords or tokens appear during login.
- Viewer controls are absent.
- Administrator confirmation is visible.
- Audit event is visible after the operation.
- Browser bookmarks and address bar contain no sensitive query values.
- OCI console, SSH configuration, tenancy identifiers, and Terraform state are not recorded.
- Verification evidence is sanitized.
- Recording stays between two and three minutes.
