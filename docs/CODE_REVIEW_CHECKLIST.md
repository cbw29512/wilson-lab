# Code Review Checklist (wilson-lab)

## Repo hygiene
- [ ] No secrets committed (.env, tokens, keys)
- [ ] Clear commit messages
- [ ] Docs updated for milestone changes

## Code headers (learning requirement)
- [ ] Every source file begins with Purpose/Why/Next header

## Security
- [ ] RBAC enforced server-side (not UI-only)
- [ ] Destructive actions require confirmation
- [ ] Audit logs written for every action

## Frontend
- [ ] UTC timestamps consistent
- [ ] Search + tag filter correct and readable
- [ ] Error states are clean

## Backend
- [ ] API contract stable
- [ ] CORS locked to known origin(s)
- [ ] Input validation on actions
