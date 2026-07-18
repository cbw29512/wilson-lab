# Live Deployment Verification

This runbook verifies that the public Wilson Lab deployment is genuinely live, correctly isolated, and behaving according to the documented security model.

The verifier uses only Python's standard library. It does not install dependencies and never writes account passwords or bearer tokens into its JSON evidence report.

## Verification levels

| Level | Purpose | State-changing operation |
|---|---|---:|
| `health` | HTTPS health response and exact CORS origin | No |
| `read-only` | Health plus authentication, inventory, details, Viewer restrictions, confirmation enforcement, and Administrator audit access | No |
| `full` | Every read-only check plus one confirmed managed operation and matching audit evidence | Yes |

The full check prefers `restart` on an already running managed demonstration container. It never sends raw Docker commands and never targets an unlabeled resource.

## What is checked

### Health

- The supplied API value is an absolute HTTPS origin.
- `GET /health` returns HTTP 200.
- `status` is `ok`.
- `environment` is `production`.
- `runtime` is `docker`.
- CORS accepts the exact GitHub Pages origin.
- CORS permits authenticated `GET` requests.

### Read-only

- Invalid credentials return HTTP 401.
- Viewer login returns an active Viewer identity.
- Viewer inventory is non-empty and structurally valid.
- Resource detail matches an inventory resource.
- Viewer audit access returns HTTP 403.
- Viewer operation access returns HTTP 403.
- Administrator login returns an active Administrator identity.
- Administrator inventory is available.
- An unconfirmed operation returns HTTP 409.
- Administrator audit history returns structurally valid events.

### Full

- A managed resource exposes an allowed operation.
- A confirmed operation succeeds.
- The response contains an integer action-request identifier.
- Audit history contains the same request identifier.
- The matching audit event reports a succeeded outcome.

## GitHub configuration

After the live API is available, add the following repository settings to `cbw29512/wilson-lab`.

### Actions variable

| Name | Value |
|---|---|
| `VITE_API_ORIGIN` | `https://YOUR_API_DOMAIN` |

Optional username variables are supported when the generated usernames were changed:

- `WILSON_LAB_VIEWER_USERNAME`
- `WILSON_LAB_ADMIN_USERNAME`

### Actions secrets

- `WILSON_LAB_VIEWER_PASSWORD`
- `WILSON_LAB_ADMIN_PASSWORD`

Use the passwords generated on the OCI VM by `deploy/scripts/prepare-secrets.sh`. Do not paste these values into issues, pull requests, workflow inputs, screenshots, or repository variables.

## Run through GitHub Actions

1. Open the Wilson Lab repository.
2. Open **Actions**.
3. Select **Live Deployment Verification**.
4. Select **Run workflow**.
5. Leave API origin blank to use `VITE_API_ORIGIN`, or enter an HTTPS origin for a one-time check.
6. Select a verification level.
7. Run the workflow.

Recommended sequence after deployment:

1. Run `health` immediately after DNS and Caddy are ready.
2. Add the two credential secrets.
3. Run `read-only`.
4. Review the resulting JSON artifact.
5. Run `full` once while observing the dashboard and audit timeline.

The workflow uploads `live-verification-report.json` as a 30-day artifact even when a verification check fails after report creation.

## Scheduled verification

The workflow runs once daily at 12:17 UTC when `VITE_API_ORIGIN` exists.

Scheduled runs always select `health` level. They do not load or require demo-account credentials and cannot request a state-changing operation.

## Run locally from Windows PowerShell

From a current clone of Wilson Lab:

```powershell
cd path\to\wilson-lab

$env:WILSON_LAB_API_ORIGIN = "https://YOUR_API_DOMAIN"
$env:WILSON_LAB_FRONTEND_ORIGIN = "https://cbw29512.github.io"

py -3.12 .\tools\verify_live.py `
  --level health `
  --report .\artifacts\live-health-report.json
```

For authenticated verification, read the passwords without displaying them:

```powershell
$ViewerSecure = Read-Host "Viewer password" -AsSecureString
$AdminSecure = Read-Host "Administrator password" -AsSecureString
$env:WILSON_LAB_VIEWER_PASSWORD = [System.Net.NetworkCredential]::new("", $ViewerSecure).Password
$env:WILSON_LAB_ADMIN_PASSWORD = [System.Net.NetworkCredential]::new("", $AdminSecure).Password

py -3.12 .\tools\verify_live.py `
  --level read-only `
  --report .\artifacts\live-read-only-report.json
```

Run the full check only against the dedicated disposable demonstration VM:

```powershell
py -3.12 .\tools\verify_live.py `
  --level full `
  --report .\artifacts\live-full-report.json
```

Clear the process environment immediately afterward:

```powershell
Remove-Item Env:WILSON_LAB_VIEWER_PASSWORD -ErrorAction SilentlyContinue
Remove-Item Env:WILSON_LAB_ADMIN_PASSWORD -ErrorAction SilentlyContinue
$ViewerSecure = $null
$AdminSecure = $null
```

## Evidence-report fields

The report contains:

- UTC generation time
- API and frontend origins
- selected verification level
- sanitized health fields
- inventory count
- resource name/identifier prefix used by a full check
- per-check pass/fail status
- per-check duration
- sanitized failure detail

The report excludes:

- Viewer and Administrator passwords
- bearer tokens
- private SSH keys
- JWT signing secrets
- Terraform state
- generated secret-file contents

Unit tests explicitly fail when known test passwords or bearer tokens appear in report serialization.

## Failure interpretation

### Configuration fails

The origin is missing, contains a path, or is not HTTPS. Supply only the origin, for example:

```text
https://api.example.com
```

### Health fails

Review:

```bash
sudo cloud-init status --long
sudo tail -n 300 /var/log/cloud-init-output.log
cd /opt/wilson-lab/deploy
docker compose ps
docker compose logs --tail=300 caddy api
```

### CORS fails

Confirm the API's production CORS setting contains the exact GitHub Pages origin:

```text
https://cbw29512.github.io
```

Do not use a wildcard origin for authenticated API access.

### Credential configuration fails

Confirm both GitHub secrets exist and contain different generated passwords.

### Inventory is empty

Confirm the demonstration containers are running and carry:

```text
wilson-lab.managed=true
```

### Viewer authorization fails

Do not rely on hidden browser buttons. A Viewer must receive HTTP 403 from both the operation and audit endpoints.

### Confirmation check fails

The API must reject an Administrator operation unless the request body contains `confirmed=true`.

### Full operation fails

Review API and Docker logs. Do not broaden the API, mount additional host paths, expose the Docker daemon over TCP, or remove label checks to make the test pass.

## Final demonstration evidence

Capture these only after health, read-only, and full verification all pass:

- dashboard showing `API: available`
- dashboard showing `Live inventory`
- Viewer identity with controls unavailable
- Administrator identity with role-aware controls
- resource detail drawer
- explicit confirmation dialog
- successful managed operation
- audit event matching that operation
- GitHub Actions verification summary
- Terraform and deployment CI success

Never include account passwords, JWTs, secret files, SSH private keys, Terraform state, Oracle tenancy identifiers, or full public-IP administration details in screenshots or recordings.
