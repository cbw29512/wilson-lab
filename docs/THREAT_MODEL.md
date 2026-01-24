# Threat Model (starter)

## Assets
- Ability to create/stop/delete/recreate lab infrastructure
- User identities (Admin/User)
- Audit log integrity

## Threats (initial)
- Unauthorized access to control plane
- Token/secret leakage (frontend is public code)
- Accidental destructive actions
- Abuse (brute-force login, spam action calls)

## Mitigations (planned)
- RBAC enforced server-side
- No secrets in frontend; use env/config on backend only
- Rate limiting + lockout policy
- Confirmations for destructive actions (type-to-confirm)
- Full audit logging
