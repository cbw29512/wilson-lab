# Wilson Lab

A security-conscious infrastructure control-plane showcase built to demonstrate product thinking, technical discovery, API design, authorization, operational safety, and clear communication.

**Live dashboard:** https://cbw29512.github.io/wilson-lab/

## What it demonstrates

- A modern React 19 and TypeScript dashboard
- Searchable and filterable infrastructure inventory
- Clear live-versus-demo data state
- FastAPI control-plane API integration
- Signed JWT authentication with session-scoped browser storage
- Viewer and Administrator roles
- Role-aware resource controls and details
- Explicit confirmation before state-changing operations
- Allowlisted start, stop, and restart actions
- SQLite-backed action requests and audit history
- Mock and Docker runtime adapters
- Frontend response validation and safe API fallback
- Automated frontend and backend CI
- Security documentation and repeatable setup instructions

## Current milestone

| Milestone | Status | Result |
|---|---|---|
| M0 — Repository foundation | Complete | Documentation, CI, Pages deployment, hooks |
| M1 — Dashboard | Complete | Resource cards, search, filters, sorting, UTC timestamps |
| M2 — Secure API foundation | Complete | Auth, RBAC, inventory, operations, audit trail, tests |
| M3 — Frontend/API integration | Complete in PR #2 | Login, live-data state, role-aware controls, confirmation, details, audit panel |
| M4 — Cloud sandbox | Next | Dedicated HTTPS-hosted demo containers and deployment runbook |

## Architecture

```mermaid
flowchart LR
    Recruiter[Recruiter browser] -->|HTTPS| UI[React dashboard\nGitHub Pages]
    UI -->|JWT API requests| API[FastAPI control plane\nDedicated sandbox VM]
    API --> DB[(SQLite audit database)]
    API --> Guard[RBAC + confirmation\nmanaged-label allowlist]
    Guard --> Runtime[Mock or Docker runtime]
    Runtime --> Containers[Dedicated demo containers]
```

The Docker adapter only sees containers labeled `wilson-lab.managed=true`. It exposes no shell execution, container creation, deletion, image pulling, or arbitrary Docker commands.

## Dashboard behavior

- The public GitHub Pages site always remains useful with validated demo inventory.
- When an API is reachable, the dashboard offers Viewer or Administrator sign-in.
- A valid session switches the inventory source to live data.
- Viewer accounts remain read-only.
- Administrator actions require explicit confirmation and refresh the audit timeline.
- Invalid or expired sessions are cleared and returned to demo mode.
- The frontend contains no embedded credentials.

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
cp .env.example .env
uvicorn app.main:app --reload --port 8055
```

PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test]"
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8055
```

### Frontend

Open a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

The Vite development server proxies `/api` and `/health` to `http://127.0.0.1:8055`.

For a hosted frontend build, set `VITE_API_ORIGIN` to the HTTPS origin of the isolated API before running `npm run build`. Leave it blank to keep the deployed dashboard in demo mode.

## Validate

```bash
cd frontend
npm ci
npm run check

cd ../backend
pip install -e ".[test]"
pytest
```

## Security model

Wilson Lab is intentionally narrow:

- Viewer accounts can inspect inventory but cannot change state.
- Administrator accounts can request only valid start, stop, or restart transitions.
- Every state-changing request requires explicit confirmation.
- Every success and failure produces an audit record.
- Docker resources are checked against the management label before use.
- The Docker-backed mode belongs on a dedicated cloud sandbox, never a home or production host.

See [`docs/SECURITY.md`](docs/SECURITY.md) for the threat model and [`backend/README.md`](backend/README.md) for API setup.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — components and trust boundaries
- [`docs/SECURITY.md`](docs/SECURITY.md) — threats, controls, and accepted risks
- [`docs/BUILD_LOG.md`](docs/BUILD_LOG.md) — chronological engineering record
- [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — interview demonstration flow
- [`backend/README.md`](backend/README.md) — API endpoints and local setup
