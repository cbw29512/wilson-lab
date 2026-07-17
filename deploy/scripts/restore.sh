#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bash deploy/scripts/restore.sh deploy/backups/wilson_lab_TIMESTAMP.db" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKUP_FILE="$(realpath "$1")"
RESTORE_PATH="/data/wilson_lab.restore.db"

[[ -f "${BACKUP_FILE}" ]] || {
  echo "Backup file not found: ${BACKUP_FILE}" >&2
  exit 1
}

cd "${DEPLOY_DIR}"

echo "Creating a pre-restore backup..."
bash "${SCRIPT_DIR}/backup.sh"

echo "Stopping the API and proxy..."
docker compose stop caddy api

restart_services() {
  docker compose up -d api caddy >/dev/null 2>&1 || true
}
trap restart_services EXIT

docker compose cp "${BACKUP_FILE}" "api:${RESTORE_PATH}"
docker compose run --rm --no-deps api python - <<'PY'
import os
import sqlite3

restore_path = "/data/wilson_lab.restore.db"
database_path = "/data/wilson_lab.db"
connection = sqlite3.connect(restore_path)
try:
    result = connection.execute("PRAGMA integrity_check").fetchone()
finally:
    connection.close()
if not result or result[0] != "ok":
    raise SystemExit("Backup failed SQLite integrity_check")
os.replace(restore_path, database_path)
PY

docker compose up -d api caddy
trap - EXIT

echo "Restore completed and services restarted."
