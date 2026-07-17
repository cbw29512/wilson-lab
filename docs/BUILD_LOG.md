# Build Log (Chronological)

Rule: every milestone ends with:
- What changed
- Why it changed
- How it was verified
- What I learned

---

## M0 — Repository scaffold

### What changed

- Created the documentation framework, workflows, and versioned git hooks.
- Configured SSH-based GitHub authentication.

### Why

Establish a repeatable project foundation before application work.

### Verification

- Repository files committed and pushed.
- GitHub SSH authentication succeeded.

### What I learned

Documentation and CI are most useful when they begin with the repository rather than being added after implementation.

---

## M1 — React inventory dashboard

### What changed

- Added a React and TypeScript dashboard.
- Added resource cards, search, tag filters, sorting, status badges, and UTC timestamps.
- Added a mock JSON inventory with an API-first fallback path.
- Added GitHub Pages deployment and frontend CI.

### Why

Create an interview-ready product surface before connecting privileged infrastructure.

### Verification

- `npm run build` succeeds.
- GitHub Actions frontend typecheck and build succeed.
- GitHub Pages deploys the dashboard.

### What I learned

A convincing infrastructure product needs a clear user experience, but the UI must not pretend planned backend capabilities are already complete.

---

## M2 — Secure control-plane foundation

### What changed

- Added a FastAPI backend with typed Pydantic models.
- Added SQLAlchemy models for users, action requests, and audit events.
- Added secure password hashing and signed JWT access tokens.
- Added Viewer and Administrator authorization.
- Added authenticated inventory and resource-detail endpoints.
- Added explicit-confirmation start, stop, and restart operations.
- Added mock and label-restricted Docker runtimes.
- Added success and failure audit records.
- Added backend packaging, tests, documentation, and CI.

### Why

Move Wilson Lab from a polished mock dashboard to a defensible control-plane architecture while limiting Docker exposure to a narrow, explainable product surface.

### Verification

- Backend package installs and compiles on Python 3.12.
- Pytest verifies authentication, roles, inventory, details, confirmation, operations, invalid transitions, and audit events.
- Pull request: `Build M2 secure control-plane API`.

### What I learned

Docker control is effectively privileged host control, so UI restrictions are not enough. The design needs sandbox isolation, server-side roles, action enums, state validation, labels, confirmation, and durable audit evidence.

---

## M3 — Frontend/API integration

### What changed

- Modularized the dashboard into typed API, session, utility, hook, component, and style layers.
- Added API reachability and live-versus-demo indicators.
- Added Viewer and Administrator sign-in.
- Added session-scoped token storage and invalid-session rejection.
- Added validated live inventory with safe demo fallback.
- Added resource details, role-aware actions, confirmation, and Administrator audit history.
- Added automatic return to demo mode after session expiration or API loss.
- Added dependency-free frontend contract tests.

### Why

Complete the product flow without allowing API downtime or missing cloud infrastructure to break the public showcase.

### Verification

- Frontend contract tests pass on Node 22.
- Strict TypeScript compilation succeeds.
- Vite creates the GitHub Pages production bundle.
- Pull request: `Connect M3 dashboard to control plane`.

### What I learned

A public showcase must communicate data provenance clearly. Demo fallback is valuable only when visitors can distinguish it from live state, and browser role controls remain a usability layer over server authorization.

---

## M4 — Cloud deployment bundle

### What changed

- Added a provider-neutral Docker Compose stack for a dedicated Ubuntu cloud VM.
- Added Caddy reverse proxy configuration with automatic HTTPS.
- Added a fixed non-root API identity and hardened container settings.
- Added file-backed JWT, Viewer, and Administrator secrets.
- Added production validation for weak, default, duplicated, missing, and unreadable secrets.
- Added two labeled demonstration services on an internal network with no public ports.
- Added persistent API and Caddy volumes.
- Added preflight, credential-display, backup, and integrity-checked restore scripts.
- Added a complete deployment and recovery runbook.
- Added deployment CI for Compose, Caddy, shell syntax, image build, and image identity.
- Updated GitHub Pages to consume the repository variable `VITE_API_ORIGIN`.

### Why

Make cloud activation repeatable and reviewable before connecting a real public VM or putting any privileged runtime behind the portfolio.

### Verification

- Backend tests cover file-backed production secret behavior.
- Deployment CI validates the resolved Compose model.
- Caddy validates the production Caddyfile.
- The API Docker image builds with user `10001:10001`.
- Shell scripts pass syntax validation.
- Pull request: `Build M4 cloud deployment bundle`.

### What I learned

Infrastructure code needs the same truthful boundaries as application code. The deployment can be fully prepared and tested in CI, while VM provisioning, DNS ownership, and final public activation remain explicit external steps.

---

## M5 — Live cloud activation (external step)

Remaining work:

- provision a dedicated cloud VM
- create the DNS record
- run the deployment preflight and start the stack
- verify HTTPS and container isolation
- set the GitHub repository variable `VITE_API_ORIGIN`
- rotate and securely store demonstration credentials
- capture final screenshots and a short demonstration recording
