# Wilson Lab Cloud Sandbox Deployment

This directory deploys Wilson Lab to a **dedicated, disposable cloud VM**. Do not run the Docker-backed control plane on a home server, workstation, production host, or any machine containing unrelated containers.

## Result

The deployment provides:

- Caddy on public ports 80 and 443
- Automatic HTTPS for a real DNS name
- FastAPI reachable only through Caddy
- Persistent SQLite audit data
- File-backed JWT and demo-account secrets
- Two isolated, labeled demonstration containers
- No public ports for the API, nginx demo, or Redis demo
- Backup, restore, credential-display, and preflight scripts

## Architecture

```text
Internet
   |
   | 80/443
   v
Caddy (automatic HTTPS)
   |
   | private Compose network
   v
FastAPI control plane ---- /var/run/docker.sock
   |                              |
   | SQLite audit volume          | only labeled resources
   v                              v
api_data                  demo-web + demo-cache
                         internal lab network only
```

The Docker socket is powerful even when mounted read-only because API requests over the socket can still change container state. Wilson Lab reduces that risk through VM isolation, server-side roles, action enums, current-state checks, resource labels, confirmation, and auditing. The VM itself remains the primary security boundary.

## Prerequisites

- A new cloud VM used only for Wilson Lab
- A supported 64-bit Ubuntu LTS release
- A DNS name such as `api.example.com`
- A DNS `A` record pointing that name to the VM's public IPv4 address
- Docker Engine and the Docker Compose plugin installed from Docker's official repository
- Git and OpenSSL

Cloud firewall or security-group ingress:

| Port | Source | Purpose |
|---|---|---|
| 22/TCP | Your current public IP only | SSH administration |
| 80/TCP | Internet | ACME validation and HTTPS redirect |
| 443/TCP | Internet | API HTTPS |
| 443/UDP | Internet | HTTP/3, optional |

Do **not** open ports 8055, 6379, or the Docker daemon.

## 1. Prepare the host

Verify Docker and Compose:

```bash
docker version
docker compose version
sudo systemctl enable --now docker
```

Allow your administrative account to use Docker, then reconnect your SSH session:

```bash
sudo usermod -aG docker "$USER"
exit
```

After reconnecting:

```bash
docker run --rm hello-world
```

## 2. Clone and configure

```bash
git clone https://github.com/cbw29512/wilson-lab.git
cd wilson-lab/deploy
cp .env.example .env
DOCKER_GID="$(stat -c '%g' /var/run/docker.sock)"
sed -i "s/^DOCKER_GID=.*/DOCKER_GID=${DOCKER_GID}/" .env
nano .env
```

Replace `API_DOMAIN=api.example.com` with the DNS name assigned to this VM. Leave the usernames unchanged for the initial demonstration unless you intentionally want different names.

## 3. Generate secrets

From the repository root:

```bash
bash deploy/scripts/prepare-secrets.sh
```

The script creates three ignored files under `deploy/secrets/`:

- `jwt_secret`
- `viewer_password`
- `admin_password`

They are owned by the API container's fixed UID/GID `10001:10001` and use mode `0400`. They are mounted only into the API container.

Display the generated demo credentials when needed:

```bash
bash deploy/scripts/show-credentials.sh
```

Do not paste these credentials into the repository, screenshots, issue comments, CI variables, or the public portfolio.

## 4. Run preflight

```bash
bash deploy/scripts/preflight.sh
```

Preflight verifies:

- Docker and Compose are available
- the Docker socket exists
- `deploy/.env` has a real domain
- `DOCKER_GID` matches the socket
- secret files exist
- the Compose model resolves successfully
- the Caddyfile validates

## 5. Start the stack

```bash
cd deploy
docker compose pull
docker compose build --pull api
docker compose up -d
docker compose ps
```

Watch startup:

```bash
docker compose logs -f caddy api
```

Validate HTTPS:

```bash
curl --fail --show-error --silent "https://${API_DOMAIN}/health"
```

Expected response:

```json
{"status":"ok","environment":"production","runtime":"docker"}
```

## 6. Confirm isolation

Only Caddy should publish host ports:

```bash
docker compose ps --format json
ss -lntup
```

Confirm that the API sees only labeled demo containers:

1. Sign in as Viewer through the dashboard or API.
2. Open `/api/v1/inventory` with the Bearer token.
3. Confirm that only `demo-web` and `demo-cache` appear.
4. Create an unrelated container without the management label and confirm it remains invisible.

## 7. Connect GitHub Pages

The Pages workflow reads the GitHub Actions repository variable `VITE_API_ORIGIN`.

In the `cbw29512/wilson-lab` repository:

1. Open **Settings**.
2. Open **Secrets and variables → Actions**.
3. Select **Variables**.
4. Create `VITE_API_ORIGIN` with the value `https://YOUR_API_DOMAIN`.
5. Re-run **Deploy Frontend to GitHub Pages**, or merge a documentation-only commit to `main`.

The frontend will then check `/health`, offer sign-in when the API is available, and continue to provide demo mode during an outage.

## Operations

### Status

```bash
cd deploy
docker compose ps
docker compose logs --tail=200 api caddy
```

### Update

```bash
cd ~/wilson-lab
git pull --ff-only
bash deploy/scripts/preflight.sh
cd deploy
docker compose pull
docker compose build --pull api
docker compose up -d --remove-orphans
```

### Backup

```bash
bash deploy/scripts/backup.sh
```

Backups are copied to `deploy/backups/`, ignored by Git, and set to mode `0600`. Copy them to encrypted off-host storage.

### Restore

```bash
bash deploy/scripts/restore.sh deploy/backups/wilson_lab_TIMESTAMP.db
```

The restore script:

1. creates a new pre-restore backup
2. stops Caddy and the API
3. copies the selected backup into the persistent volume
4. runs SQLite `integrity_check`
5. atomically replaces the database
6. restarts the API and Caddy

### Rotate credentials

Stop the API, remove the selected secret file, regenerate it, and recreate the API:

```bash
cd deploy
docker compose stop api
sudo rm secrets/viewer_password secrets/admin_password secrets/jwt_secret
cd ..
bash deploy/scripts/prepare-secrets.sh
cd deploy
docker compose up -d --force-recreate api
bash scripts/show-credentials.sh
```

Rotating the JWT secret immediately invalidates all active sessions.

## Recovery and troubleshooting

### Caddy cannot obtain a certificate

- Confirm the DNS record resolves to this VM.
- Confirm inbound TCP 80 and 443 are open.
- Confirm no other host service occupies those ports.
- Review `docker compose logs caddy`.

### API reports Docker inventory unavailable

```bash
stat -c '%g %A %n' /var/run/docker.sock
grep '^DOCKER_GID=' deploy/.env
docker compose exec api id
```

The socket GID and configured supplemental group must match.

### API enters a restart loop

```bash
docker compose logs --tail=200 api
sudo ls -ln deploy/secrets
```

Production startup intentionally fails when secrets are absent, unreadable, too short, duplicated, or left at development defaults.

### Emergency shutdown

```bash
cd deploy
docker compose down
```

This preserves named volumes. Do not use `docker compose down -v` unless you intend to erase the database and Caddy certificate state.
