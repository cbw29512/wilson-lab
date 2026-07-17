# Wilson Lab API

FastAPI control plane for the Wilson Lab showcase. The API provides authenticated inventory, Viewer/Admin roles, allowlisted resource operations, action tracking, and an audit trail.

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

Docker daemon access is still highly privileged. Run the Docker-backed API only on a dedicated sandbox host, protect the API with HTTPS, use strong secrets, restrict network access, and never connect it to the home lab or a production Docker host.

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

- health endpoint availability
- rejected invalid credentials
- JWT-backed Viewer identity
- authentication-required inventory
- Viewer read access
- Admin-only operations
- explicit confirmation
- valid state transitions
- rejected invalid transitions
- success and failure audit records

## API endpoints

| Method | Path | Access | Purpose |
|---|---|---|---|
| `GET` | `/health` | Public | Runtime health |
| `POST` | `/api/v1/auth/token` | Public | OAuth2 password login |
| `GET` | `/api/v1/auth/me` | Viewer/Admin | Current identity |
| `GET` | `/api/v1/inventory` | Viewer/Admin | Managed inventory |
| `GET` | `/api/v1/inventory/{id}` | Viewer/Admin | Resource details |
| `POST` | `/api/v1/resources/{id}/operations` | Admin | Confirmed safe operation |
| `GET` | `/api/v1/audit` | Admin | Recent audit events |

Interactive API documentation is available at `/docs` while the API is running.

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

Do not expose an unauthenticated Docker TCP socket. For the first cloud demonstration, run the API on the same dedicated VM and allow its service account to access the local Unix socket. Treat that account as privileged and keep the VM isolated from personal and production systems.

## Production checklist

- Generate a long random `WILSON_LAB_JWT_SECRET`.
- Replace both demo passwords.
- Set `WILSON_LAB_ENVIRONMENT=production`.
- Set CORS to the exact GitHub Pages origin.
- Put the API behind HTTPS.
- Restrict inbound traffic to required ports.
- Use a dedicated sandbox VM.
- Label only demonstration containers.
- Back up or rotate the audit database as appropriate.
- Never mount home or production directories into demonstration containers.
