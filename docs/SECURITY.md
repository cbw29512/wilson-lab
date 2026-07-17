# Wilson Lab Security Model

## Objective

Wilson Lab demonstrates controlled infrastructure operations without exposing a general-purpose Docker administration interface.

## Protected assets

- Docker host integrity
- Demonstration container state
- API credentials and signing secret
- User role assignments
- Action and audit history
- Public demonstration availability
- HTTPS certificate state and database backups

## Trust boundaries

1. The React dashboard is public static code and contains no secrets.
2. Credentials are exchanged only with the HTTPS API.
3. Caddy is the only service publishing host ports.
4. The API validates identity and role on the server.
5. The runtime accepts structured operations, never raw commands.
6. The Docker adapter can operate only containers carrying the management label.
7. Demo containers publish no host ports and use an internal network.
8. The cloud VM is isolated from home, work, and production systems.

## Roles

### Viewer

- Sign in
- View managed inventory and resource details
- Cannot change resource state
- Cannot access audit history

### Administrator

- All Viewer capabilities
- Request valid start, stop, and restart operations
- Must explicitly confirm every operation
- View recent audit history

## Allowed operations

| Current state | Allowed operations |
|---|---|
| Running | Stop, restart |
| Stopped | Start |
| Planned, error, unknown | None |

The API does not support shell execution, container creation or deletion, image pulls, arbitrary Docker calls, host-path selection, privileged-mode changes, volume or network reconfiguration, or access to unlabeled containers.

## Audit behavior

Every accepted Administrator operation creates an action request and audit event containing the actor, resource, operation, request identifier, timestamps, outcome, source address, and failure detail when applicable. Failed transitions are retained as well as successes.

## Primary threats and controls

| Threat | Control |
|---|---|
| Unauthenticated access | Bearer token required for inventory and operations |
| Viewer attempts an operation | Server-side Administrator check returns 403 |
| Accidental click | Explicit confirmation required |
| Arbitrary container selection | Management label checked during listing and before use |
| Invalid transition | Actions derived from current resource state |
| Raw command injection | API accepts an enum, not a command string |
| Secret committed to Git | Ignored file-backed secrets mounted only into the API |
| Weak production credential | Startup rejects defaults, short values, and duplicate passwords |
| API exposed directly | Only Caddy publishes ports |
| Demo service exposed publicly | No host ports and an internal lab network |
| Public Docker daemon | Unix socket only; no TCP daemon listener |
| Compromise reaches personal systems | Disposable cloud VM with no home or production connectivity |
| Database corruption | Online SQLite backups and integrity-checked restores |
| Action denial or dispute | Persistent action requests and audit records |

## Container hardening

The deployment bundle uses a fixed non-root API identity, read-only root filesystems, limited writable volumes, temporary scratch filesystems, dropped capabilities where compatible, `no-new-privileges`, resource limits, private service networking, and Caddy-managed HTTPS.

## Accepted risks

Docker daemon access remains highly privileged. A read-only socket mount does not make Docker API operations read-only. Application allowlisting narrows exposed behavior but does not make a compromised API harmless. The Docker-backed API must run only on a disposable, dedicated sandbox with no sensitive data.

SQLite is appropriate for this single-instance showcase but is not a tamper-proof or highly available audit system. A production product would use managed identity, centralized append-only logging, external secret management, rate limiting, database migrations, stronger session controls, and a separate policy layer.

## Deployment requirements

- dedicated cloud sandbox VM
- supported Ubuntu LTS release
- DNS name resolving to the VM
- public TCP 80 and 443 only, with SSH limited to the administrator's IP
- no public API, Redis, nginx, or Docker daemon ports
- file-backed random secrets
- exact GitHub Pages CORS origin
- only demonstration containers labeled as managed
- encrypted off-host backups
- routine patching, credential rotation, and disposable rebuilds

See [`../deploy/README.md`](../deploy/README.md) for the operational runbook.
