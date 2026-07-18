# Changelog

Wilson Lab follows semantic versioning for documented showcase releases. Dates use the user's America/New_York timezone.

## [0.8.0] — 2026-07-17

### Added

- React 19 and TypeScript infrastructure dashboard with validated demo fallback
- FastAPI control plane with Viewer and Administrator roles
- Signed JWT authentication and Argon2 password hashing
- Allowlisted start, stop, and restart operations with explicit confirmation
- SQLite-backed action requests and audit events
- Mock and Docker runtime adapters restricted by `wilson-lab.managed=true`
- Caddy HTTPS deployment with hardened Docker Compose services
- File-backed production secrets, backup, restore, and preflight workflows
- OCI Terraform for the VCN, subnet, firewall, A1 Flex VM, Ubuntu image selection, and cloud-init
- Credential-safe live verification at health, read-only, and full-operation levels
- Sanitized JSON and recruiter-readable Markdown evidence bundles
- Failed-login throttling with `Retry-After`
- Request IDs, no-store API responses, and separate liveness/readiness endpoints
- Backend and frontend dependency-audit workflows
- Security policy, contribution guide, issue forms, and pull-request template

### Security

- Production rejects default, weak, duplicate, missing, unreadable, or empty secrets
- Production disables interactive API documentation and OpenAPI discovery
- Viewer accounts cannot operate resources or view audit history
- Every successful or failed state-changing operation creates an audit event
- Caddy adds HSTS, CSP, framing, referrer, permissions, and content-type protections
- Scheduled verification remains health-only and cannot change container state
- Dependency audits found zero known vulnerabilities in the audited release dependencies

### Known external activation boundary

The public dashboard is available in validated demo mode. A live API still requires the repository owner's OCI account activation, Resource Manager Apply, DNS record, GitHub secrets, and `VITE_API_ORIGIN` repository variable.

## Release links

- Dashboard: https://cbw29512.github.io/wilson-lab/
- Repository: https://github.com/cbw29512/wilson-lab
- Case study: [`docs/CASE_STUDY.md`](docs/CASE_STUDY.md)
- Build history: [`docs/BUILD_LOG.md`](docs/BUILD_LOG.md)
