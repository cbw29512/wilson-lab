# Architecture (wilson-lab)

## Goal
Build a cyber lab orchestrator that looks and behaves like a professional internal platform.

## Target v1 (all online)
- **UI**: GitHub Pages (static React)
- **API**: Oracle Always Free VM (FastAPI)
- **Lab runtime**: Docker Compose on the same Oracle VM

## Trust boundaries (important for security interviews)
- Public UI code (Pages) contains **no secrets**
- API requires authentication and enforces RBAC server-side
- Destructive actions require confirmations + audit logs

## Next update
After M1/M2, add real diagrams and endpoint list.
