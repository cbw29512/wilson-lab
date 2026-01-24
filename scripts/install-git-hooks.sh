#!/usr/bin/env bash
set -euo pipefail

# Purpose:
#   Configure this repo to use versioned hooks stored under scripts/git-hooks.
# Why:
#   Default .git/hooks is not committed. core.hooksPath lets us version hooks safely.

git config core.hooksPath scripts/git-hooks
echo "✅ core.hooksPath set to scripts/git-hooks"
echo "✅ post-commit hook will auto-push after each commit (disable with WILSONLAB_NO_AUTOPUSH=1)"
