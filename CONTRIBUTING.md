# Contributing to Wilson Lab

Wilson Lab is a focused portfolio project. Contributions should strengthen the existing product story: safe infrastructure visibility, narrow operations, verifiable authorization, durable audit evidence, and repeatable deployment.

## Before changing code

1. Read `README.md`, `docs/ARCHITECTURE.md`, and `docs/SECURITY.md`.
2. Confirm the change does not broaden Docker access beyond the documented allowlist.
3. Keep planned features separate from completed claims.
4. Never commit credentials, cloud identifiers, generated secrets, Terraform state, verification artifacts containing sensitive data, or private infrastructure details.

## Development setup

### Frontend

```bash
cd frontend
npm ci
npm run check
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pytest
```

PowerShell activation:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Verification tooling

```bash
python -m unittest discover -s tools/tests -v
python tools/verify_live.py --help
python tools/render_evidence.py --help
```

### Deployment and infrastructure

```bash
docker compose --project-directory deploy -f deploy/compose.yaml config
terraform -chdir=infra/oci fmt -check
terraform -chdir=infra/oci init -backend=false
terraform -chdir=infra/oci validate
```

## Pull requests

A pull request should include:

- the problem being solved
- the security boundary affected
- the exact files and behavior changed
- tests or validation evidence
- documentation updates when claims, configuration, or operations change
- a clear statement of anything still planned or externally blocked

Keep source files focused and under roughly 150 lines where practical. Split API routes, state logic, data schemas, and UI presentation into separate modules rather than growing one large file.

## Security-sensitive changes

Changes to authentication, authorization, Docker access, secrets, cloud networking, Caddy, Terraform, audit evidence, or GitHub Actions require explicit tests. Do not weaken a failing security test simply to make CI green.

Report actual vulnerabilities privately through `SECURITY.md` rather than opening a public issue.
