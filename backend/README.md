# Wilson Lab API

FastAPI control plane for the Wilson Lab showcase. The API provides authenticated inventory, Viewer/Admin roles, allowlisted resource operations, action tracking, audit history, request correlation, login throttling, and deployment readiness checks.

## Security boundary

The Docker runtime only returns containers labeled:

```text
wilson-lab.managed=true
```

A selected container is checked for that label again before any operation. The API exposes only:

- `start`
- `stop`
- `restart`

It does not expose container creation, deletion, image pulls, shell execution, arbitrary Docker commands, or host filesystem access.

Docker daemon access is still highly privileged. Run the Docker-backed API only on a dedicated sandbox host, protect the API with HTTPS, use strong secrets, restrict network access, and never connect it to a home, employer, or production Docker host.

## Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
cp .env.example .env
uvicorn app.main:app --reload --port 8055
```

PowerShell activation:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test]"
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8055
```

The default `mock` runtime is intentionally safe and does not require Docker.

## Test

```bash
cd backend
pytest
```

Tests verify:

- liveness and readiness endpoints
- database and runtime readiness
- rejected invalid credentials
- failed-login throttling and `Retry-After`
- JWT-backed Viewer identity
- authentication-required inventory
- Viewer read access
- Admin-only operations
- explicit confirmation
- valid and invalid state transitions
- success and failure audit records
- request-correlation and no-cache headers
- production rejection of default or duplicate credentials
- file-backed secret loading

## API endpoints

| Method | Path | Access | Purpose |
|---|---|---|---|
| `GET` | `/health` | Public | Process liveness and configured mode |
| `GET` | `/ready` | Public | Database and managed-runtime readiness |
| `POST` | `/api/v1/auth/token` | Public | OAuth2 password login with failed-attempt throttling |
| `GET` | `/api/v1/auth/me` | Viewer/Admin | Current identity |
| `GET` | `/api/v1/inventory` | Viewer/Admin | Managed inventory |
| `GET` | `/api/v1/inventory/{id}` | Viewer/Admin | Resource details |
| `POST` | `/api/v1/resources/{id}/operations` | Admin | Confirmed safe operation |
| `GET` | `/api/v1/audit` | Admin | Recent audit events |

Interactive API documentation is available at `/docs` in development and test environments. Production disables `/docs`, `/redoc`, and the OpenAPI endpoint.

## Login throttling

Failed logins are limited by client IP and normalized username. Defaults:

```text
WILSON_LAB_LOGIN_ATTEMPT_LIMIT=5
WILSON_LAB_LOGIN_WINDOW_SECONDS=60
```

The attempt that reaches the limit returns `429 Too Many Requests` with `Retry-After`. A successful login clears prior failures for that key.

This limiter is deliberately single-process and in-memory because Wilson Lab deploys as one API process on one showcase VM. A horizontally scaled production system would move this control to a shared store or managed edge service.

## Request and response hardening

- Every response receives a generated `X-Request-ID` for troubleshooting.
- API responses receive `Cache-Control: no-store`.
- Responses receive `X-Content-Type-Options: nosniff`.
- Caddy adds TLS, HSTS, framing, referrer, permissions, and content-security headers.
- Caddy and Docker health checks use `/ready`, not only process liveness.

## Docker-backed runtime

Set:

```text
WILSON_LAB_RUNTIME_MODE=docker
```

Only dedicated sandbox containers should receive the management label. Example:

```bash
docker run -d \
  --name wilson-demo-nginx \
  --label wilson-lab.managed=true \
  --label wilson-lab.description="Safe Wilson Lab demonstration service" \
  --label wilson-lab.tags="demo,web,managed" \
  --label wilson-lab.environment=sandbox \
  nginx:alpine
```

Do not expose an unauthenticated Docker TCP socket. Run the API on the same dedicated VM and allow its service account to access the local Unix socket. Treat that account as privileged and keep the VM isolated from personal and production systems.

## File-backed production secrets

Wilson Lab accepts either direct values or file paths:

| Direct setting | File alternative |
|---|---|
| `WILSON_LAB_JWT_SECRET` | `WILSON_LAB_JWT_SECRET_FILE` |
| `WILSON_LAB_VIEWER_PASSWORD` | `WILSON_LAB_VIEWER_PASSWORD_FILE` |
| `WILSON_LAB_ADMIN_PASSWORD` | `WILSON_LAB_ADMIN_PASSWORD_FILE` |

When a file setting is present, its trimmed contents replace the direct value. Production startup fails when secrets are missing, unreadable, empty, too short, duplicated, or left at development defaults.

The provider-neutral Compose deployment uses files mounted under `/run/secrets/`. See [`../deploy/README.md`](../deploy/README.md).

## Production checklist

- Use file-backed random secrets.
- Set `WILSON_LAB_ENVIRONMENT=production`.
- Set CORS to the exact GitHub Pages origin.
- Keep login thresholds explicit and monitored.
- Put the API behind HTTPS.
- Restrict inbound traffic to required ports.
- Use a dedicated sandbox VM.
- Label only demonstration containers.
- Back up the audit database.
- Never mount home or production directories into demonstration containers.
