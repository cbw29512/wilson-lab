# Wilson Lab

[![Frontend CI](https://github.com/cbw29512/wilson-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/cbw29512/wilson-lab/actions/workflows/ci.yml)
[![Backend CI](https://github.com/cbw29512/wilson-lab/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/cbw29512/wilson-lab/actions/workflows/backend-ci.yml)
[![Deployment CI](https://github.com/cbw29512/wilson-lab/actions/workflows/deployment-ci.yml/badge.svg)](https://github.com/cbw29512/wilson-lab/actions/workflows/deployment-ci.yml)
[![Dependency Audit](https://github.com/cbw29512/wilson-lab/actions/workflows/dependency-audit.yml/badge.svg)](https://github.com/cbw29512/wilson-lab/actions/workflows/dependency-audit.yml)
[![Release Check](https://github.com/cbw29512/wilson-lab/actions/workflows/release-check.yml/badge.svg)](https://github.com/cbw29512/wilson-lab/actions/workflows/release-check.yml)

A security-conscious infrastructure control-plane showcase built to demonstrate product thinking, technical discovery, API design, authorization, operational safety, infrastructure as code, deployment verification, and clear communication.

**[Open the live dashboard](https://cbw29512.github.io/wilson-lab/)** · **[Read the case study](docs/CASE_STUDY.md)** · **[Review the changelog](CHANGELOG.md)**

> The public dashboard is live in validated demo mode. The private cloud API is fully prepared and tested but still requires the repository owner's OCI account, DNS, and GitHub-secret activation.

## At a glance

| Area | Implementation |
|---|---|
| Product | Searchable infrastructure dashboard with explicit demo/live provenance |
| Frontend | React 19, TypeScript, Vite, runtime response validation |
| API | FastAPI, JWT authentication, Viewer/Admin RBAC, readiness checks |
| Safety | Confirmation, state validation, login throttling, Docker label allowlist |
| Evidence | SQLite audit trail plus sanitized JSON and Markdown proof bundles |
| Deployment | Hardened Docker Compose, Caddy HTTPS, file-backed secrets |
| Cloud | OCI Terraform and Resource Manager packaging |
| Quality | Frontend, backend, deployment, infrastructure, verification, audit, and release CI |
| Release | `0.8.0` |

## Why this project matters

Wilson Lab demonstrates more than framework familiarity. It shows how to translate privileged infrastructure access into a product that customers and stakeholders can understand:

- make data provenance obvious instead of presenting demo data as live
- enforce roles on the server rather than trusting browser controls
- reduce a powerful Docker integration to three explainable operations
- require confirmation and record both successes and failures
- keep the public experience useful during API downtime
- automate deployment, verification, dependency review, and release evidence
- state external blockers honestly rather than overstating completion

That combination is directly relevant to Sales Engineer, Solutions Consultant, Technical Account Manager, implementation, and customer-facing infrastructure roles.

## What it demonstrates

- A modern React 19 and TypeScript dashboard
- Searchable and filterable infrastructure inventory
- Clear live-versus-demo data state
- FastAPI control-plane API integration
- Signed JWT authentication with session-scoped browser storage
- Viewer and Administrator roles
- Failed-login throttling with `Retry-After`
- Request IDs and non-cacheable API responses
- Separate liveness and database/runtime readiness checks
- Role-aware resource controls and details
- Explicit confirmation before state-changing operations
- Allowlisted start, stop, and restart actions
- SQLite-backed action requests and audit history
- Mock and Docker runtime adapters
- Frontend response validation and safe API fallback
- Automatic HTTPS deployment through Caddy
- File-backed production secrets
- Backup and integrity-checked restore workflows
- Terraform-managed Oracle Cloud network and compute resources
- Credential-safe live deployment verification and recruiter evidence
- Automated frontend, backend, deployment, infrastructure, verification, dependency-audit, and release CI

## Current milestone

| Milestone | Status | Result |
|---|---|---|
| M0 — Repository foundation | Complete | Documentation, CI, Pages deployment, hooks |
| M1 — Dashboard | Complete | Resource cards, search, filters, sorting, UTC timestamps |
| M2 — Secure API foundation | Complete | Auth, RBAC, inventory, operations, audit trail, tests |
| M3 — Frontend/API integration | Complete | Login, live-data state, role-aware controls, confirmation, details, audit panel |
| M4 — Cloud deployment bundle | Complete | Caddy HTTPS, hardened Compose stack, secrets, backups, preflight, deployment CI |
| M5 — OCI infrastructure as code | Complete | VCN, firewall, A1 VM, Ubuntu image selection, cloud-init, Resource Manager runbook |
| M6 — Live verification tooling | Complete in PR #6 | Health, RBAC, confirmation, operation, audit, redaction tests, scheduled monitoring |
| M7 — Recruiter evidence | Complete in PR #7 | Sanitized JSON, validated Markdown proof bundle, three-minute demo script |
| M8 — API and repository hardening | Complete in PR #8 | Login throttling, readiness, request IDs, dependency audits, security contribution policy |
| Release 0.8.0 | Prepared | Version contract, changelog, case study, release manifest, CI badges |
| M9 — Live activation | External step | Activate OCI account, apply stack, create DNS record, connect Pages to API |

## Architecture

```mermaid
flowchart LR
    Recruiter[Recruiter browser] -->|HTTPS| UI[React dashboard\nGitHub Pages]
    UI -->|JWT API requests| Proxy[Caddy\nAutomatic HTTPS]
    Proxy --> API[FastAPI control plane\nDedicated OCI VM]
    API --> DB[(SQLite audit volume)]
    API --> Guard[RBAC + confirmation\nrate limit + label allowlist]
    Guard --> Runtime[Docker socket\nVM-local only]
    Runtime --> Containers[Isolated labeled\ndemo containers]
    IaC[Terraform / OCI Resource Manager] --> Cloud[VCN + subnet + firewall\nA1 Flex Ubuntu VM]
    Cloud --> Proxy
    Verify[Credential-safe verifier\nGitHub Actions or PowerShell] --> Proxy
```

The Docker adapter only sees containers labeled `wilson-lab.managed=true`. It exposes no shell execution, container creation, deletion, image pulling, or arbitrary Docker commands. The Docker-backed stack belongs only on a dedicated disposable VM.

## Dashboard behavior

- The public GitHub Pages site always remains useful with validated demo inventory.
- When an API is reachable, the dashboard offers Viewer or Administrator sign-in.
- A valid session switches the inventory source to live data.
- Viewer accounts remain read-only.
- Administrator actions require explicit confirmation and refresh the audit timeline.
- Invalid or expired sessions are cleared and returned to demo mode.
- The frontend contains no embedded credentials.

## Local quick start

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

The Vite development server proxies `/api`, `/health`, and `/ready` to `http://127.0.0.1:8055`.

## Cloud deployment

Two versioned layers make activation repeatable:

1. [`infra/oci/`](infra/oci/README.md) provisions the Oracle Cloud VCN, subnet, firewall, public IP, and Ubuntu A1 Flex instance through Terraform or OCI Resource Manager.
2. [`deploy/`](deploy/README.md) installs Caddy, the API, persistent data, secrets, backups, and isolated demonstration containers on that VM.

The OCI Terraform module includes:

- Resource Manager and local API-key authentication modes
- dynamically selected Canonical Ubuntu ARM image
- SSH limited to one `/32` administrator address
- public web ingress limited to ports 80 and 443
- a 1 OCPU / 6 GB / 50 GB default configuration
- cloud-init that installs Docker and starts Wilson Lab
- Terraform formatting and validation CI
- a packaged Resource Manager artifact

Actual activation still requires an OCI account and a DNS name controlled by the user.

## Live verification

[`tools/verify_live.py`](tools/verify_live.py) verifies the deployed security and product contract at three levels:

- `health`: HTTPS health response and exact CORS origin
- `read-only`: authentication, inventory, resource details, Viewer restrictions, confirmation enforcement, and Administrator audit access
- `full`: one confirmed managed operation plus matching audit evidence

The scheduled GitHub Actions run is health-only and cannot change container state. Authenticated checks require repository secrets, and generated JSON and Markdown evidence exclude passwords and bearer tokens.

See [`docs/LIVE_VERIFICATION.md`](docs/LIVE_VERIFICATION.md) for GitHub Actions and PowerShell procedures.

## Validate

```bash
cd frontend
npm ci
npm run check
npm audit --omit=dev --audit-level=high

cd ../backend
pip install -e ".[test]"
pytest

cd ../infra/oci
terraform fmt -check
terraform init -backend=false
terraform validate

cd ../..
python -m compileall -q tools
python -m unittest discover -s tools/tests -v
```

Deployment CI separately validates the Compose stack, Caddyfile, shell scripts, hardened API image, and non-root container identity. Dependency Audit runs on relevant pull requests, changes to `main`, manual dispatch, and a weekly schedule. Release Check verifies that `VERSION`, the backend package, the changelog, the case study, and any future `v*` tag agree.

## Security model

Wilson Lab is intentionally narrow:

- Failed logins are limited by client IP and normalized username.
- Viewer accounts can inspect inventory but cannot change state.
- Administrator accounts can request only valid start, stop, or restart transitions.
- Every state-changing request requires explicit confirmation.
- Every success and failure produces an audit record.
- Docker resources are checked against the management label before use.
- Production startup rejects weak, default, duplicate, missing, or unreadable secrets.
- Production disables interactive API documentation and OpenAPI discovery.
- API responses receive generated request IDs, no-store caching, and defensive headers.
- Caddy uses readiness checks and adds HTTPS security headers.
- OCI security rules expose SSH only to a supplied `/32` and web traffic only on 80/443.
- Live verification reports redact bearer tokens and never include configured passwords.
- Scheduled monitoring performs no authenticated or state-changing requests.
- The Docker-backed mode belongs on a dedicated cloud sandbox, never a home, employer, or production host.

Read [`SECURITY.md`](SECURITY.md) before reporting a vulnerability and [`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing changes. Detailed controls are in [`docs/SECURITY.md`](docs/SECURITY.md), [`backend/README.md`](backend/README.md), [`deploy/README.md`](deploy/README.md), [`infra/oci/README.md`](infra/oci/README.md), and [`docs/LIVE_VERIFICATION.md`](docs/LIVE_VERIFICATION.md).

## Documentation

- [`docs/CASE_STUDY.md`](docs/CASE_STUDY.md) — recruiter-facing problem, decisions, tradeoffs, evidence, and value
- [`CHANGELOG.md`](CHANGELOG.md) — versioned release history and activation boundary
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — components and trust boundaries
- [`docs/SECURITY.md`](docs/SECURITY.md) — threats, controls, and accepted risks
- [`docs/BUILD_LOG.md`](docs/BUILD_LOG.md) — chronological engineering record
- [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — interview demonstration flow
- [`docs/LIVE_VERIFICATION.md`](docs/LIVE_VERIFICATION.md) — live health, RBAC, operation, audit, and evidence checks
- [`backend/README.md`](backend/README.md) — API endpoints and local setup
- [`deploy/README.md`](deploy/README.md) — cloud deployment and recovery runbook
- [`infra/oci/README.md`](infra/oci/README.md) — Oracle Resource Manager and Terraform activation
