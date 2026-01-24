# Decisions (ADR-lite)

We record *why* we chose things. This is interview gold.

## M0 — GitHub Pages + separate backend
- GitHub Pages hosts static UI only.
- The API must run elsewhere (Oracle Always Free VM).

## M0.1 — GitHub auth method: SSH over HTTPS
- HTTPS pushes require PAT tokens; password auth is not supported.
- Chosen: SSH keys to avoid repeated token prompts and support a smoother workflow.
