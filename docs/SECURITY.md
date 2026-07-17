# Wilson Lab Security Model

## Objective

Wilson Lab demonstrates controlled infrastructure operations without exposing a general-purpose Docker administration interface.

## Protected assets

- Docker host integrity
- Demonstration container state
- API credentials and signing secret
- User role assignments
- Action and audit history
- Availability of the public demonstration

## Trust boundaries

1. The React dashboard is public static code and contains no secrets.
2. Credentials are exchanged only with the HTTPS API.
3. The API validates identity and role on the server.
4. The runtime adapter accepts structured operations, never raw commands.
5. The Docker adapter can inspect or operate only containers carrying the configured management label.
6. The demonstration VM is isolated from home, work, and production systems.

## Roles

### Viewer

- Sign in
- View managed inventory
- View resource details
- Cannot perform state-changing operations
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

The API does not support:

- shell or command execution
- container creation or deletion
- image pulling or building
- arbitrary Docker API calls
- host path selection
- privileged mode changes
- volume or network reconfiguration
- access to unlabeled containers

## Audit behavior

Every accepted Administrator operation creates an action request. The request records:

- resource identifier
- requested operation
- requesting user
- request and completion timestamps
- success or failure
- error detail when applicable

A corresponding audit event records the actor, resource, outcome, source address, and action-request identifier. Failed state transitions are audited as well as successful ones.

## Primary threats and controls

| Threat | Control |
|---|---|
| Unauthenticated access | OAuth2 bearer token required for inventory and operations |
| Viewer attempts an operation | Server-side Administrator dependency returns 403 |
| Accidental click | Explicit `confirmed=true` required |
| Arbitrary container selection | Management label checked during listing and again before use |
| Invalid transition | Allowed actions derived from current resource state |
| Raw Docker command injection | API accepts an enum, not a command string |
| Secret committed to Git | Environment variables and `.env.example` placeholders |
| Public Docker daemon exposure | Local Unix socket only; no unauthenticated TCP daemon |
| Compromise reaches personal systems | Dedicated cloud sandbox with no home or production connectivity |
| Action denial or dispute | Persistent action request and audit records |

## Accepted risks

Docker daemon access remains highly privileged. Application-level allowlisting reduces exposed functionality but does not make a compromised API process harmless. The Docker-backed API must therefore run only in a disposable, dedicated sandbox environment with no sensitive data.

SQLite is appropriate for the single-instance demonstration but is not presented as a high-availability audit system. A production product would use managed identity, centralized logging, secret management, rate limiting, database migrations, stronger session controls, and a separate policy-enforcement layer.

## Deployment requirements

- HTTPS at the public edge
- Long random JWT signing secret
- Replaced Viewer and Administrator passwords
- Exact CORS origin
- Dedicated sandbox VM
- Firewall allowing only SSH administration and HTTPS service traffic
- No public Docker daemon port
- No sensitive host mounts
- Only demonstration containers labeled as managed
- Routine rebuild or rotation of the disposable environment
