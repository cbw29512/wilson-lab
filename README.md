# wilson-lab

## Purpose
wilson-lab is an interview-ready cyber lab orchestrator:
- **Frontend**: React “clean SaaS dashboard” (hosted on GitHub Pages)
- **Backend**: Control plane API (Oracle Always Free VM) to manage Docker + (later) VMs
- **Security**: Admin/User roles, RBAC, audit logs, safety rails for destructive actions

## Milestones (high level)
- **M0**: Repo scaffold + docs + CI + Pages workflow + hooks
- **M1**: Dashboard UI (cards + UTC timestamps + search + tag filters)
- **M2**: Online backend + Docker inventory API
- **M3**: Auth (Admin/User) + RBAC + audit log
- **M4**: One-click recreate + health + offline-ish image caching

## Documentation
Start here:
- `docs/BUILD_LOG.md` (chronological journal)
- `docs/ARCHITECTURE.md` (system overview)
- `docs/DEMO_SCRIPT.md` (how to demo this like a product)
