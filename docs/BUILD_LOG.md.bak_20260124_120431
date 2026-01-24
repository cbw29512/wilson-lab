# Build Log (Chronological)

Rule: every milestone ends with:
- What changed
- Why it changed
- How it was verified (commands/screenshots)
- What I learned

---

## M0 — Repo scaffold
- Created documentation framework, workflows, and versioned git hooks.
- Verified: files exist, git status clean, commit pushed.

### M0.1 — GitHub authentication (SSH) + first push
- Problem: HTTPS push failed because GitHub does not allow password auth for Git operations.
- Solution: Switched repo remote to SSH, authenticated with existing ed25519 key.
- Commands:
  - `ssh -T git@github.com` (verified auth)
  - `git remote set-url origin git@github.com:cbw29512/wilson-lab.git`
  - `git push -u origin main` (verified push + upstream tracking)
- Verification evidence:
  - GitHub SSH test returned: "You've successfully authenticated"
  - Push created `main -> main` and set upstream tracking.
