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
- Added `MockRuntime` for safe development and CI.
- Added `DockerRuntime` restricted to `wilson-lab.managed=true` containers.
- Added success and failure audit records.
- Added a backend Dockerfile, environment template, API documentation, threat model, and CI workflow.

### Why

Move Wilson Lab from a polished mock dashboard to a defensible control-plane architecture while limiting Docker exposure to a narrow, explainable product surface.

### Verification

- Frontend typecheck and production build pass in GitHub Actions.
- Backend package installs on Python 3.12.
- Every backend module compiles.
- Pytest verifies authentication, roles, inventory, resource details, confirmation, valid operations, invalid transitions, and audit events.
- Pull request: `Build M2 secure control-plane API`.

### What I learned

Docker control is effectively privileged host control, so UI-level restrictions are not enough. The design needs multiple controls: dedicated sandbox isolation, server-side roles, structured action enums, current-state validation, management labels, confirmation, and durable audit evidence.

---

## M3 — Frontend/API integration

### What changed

- Replaced the single 209-line dashboard component with typed API, session, utility, hook, component, and style modules.
- Added API reachability and live-versus-demo indicators.
- Added Viewer and Administrator sign-in.
- Added session-scoped token storage and invalid-session rejection.
- Added validated live inventory with safe demo fallback.
- Added resource details, role-aware actions, confirmation, and Administrator audit history.
- Added automatic return to demo mode after session expiration or API loss.
- Added dependency-free Node tests for resource filtering, UTC formatting, and session persistence safeguards.
- Updated frontend CI to run tests before TypeScript and Vite builds.

### Why

Complete the user-facing product flow without allowing API downtime or missing cloud infrastructure to break the public showcase.

### Verification

- Frontend contract tests pass on Node 22.
- TypeScript compilation succeeds with strict settings.
- Vite creates the GitHub Pages production bundle.
- Pull request: `Connect M3 dashboard to control plane`.

### What I learned

A public showcase should communicate data provenance clearly. Demo fallback is valuable only when visitors can distinguish it from live state, and browser role controls must remain a usability layer on top of server-enforced authorization.

---

## M4 — Cloud sandbox (next)

Planned work:

- Provision a dedicated cloud VM with HTTPS
- Deploy the FastAPI service and SQLite persistence
- Add only labeled demonstration containers
- Configure CORS and production `VITE_API_ORIGIN`
- Replace local demo credentials with rotated cloud credentials
- Add reverse-proxy, backup, recovery, and deployment runbooks
- Capture final screenshots and a short demonstration recording
