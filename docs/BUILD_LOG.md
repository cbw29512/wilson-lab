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

## M3 — Frontend/API integration (next)

Planned work:

- Login experience for Viewer and Administrator demo accounts
- Clear live-versus-mock data indicator
- Token-aware API client
- Resource detail drawer
- Role-aware operation buttons
- Confirmation dialog
- Audit timeline for Administrators
- Loading, expiration, and API-unavailable states
- Frontend tests for critical user flows
