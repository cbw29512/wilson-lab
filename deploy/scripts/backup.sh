#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKUP_DIR="${DEPLOY_DIR}/backups"
STAMP="$(date -u +'%Y%m%dT%H%M%SZ')"
FILE_NAME="wilson_lab_${STAMP}.db"
CONTAINER_PATH="/data/backups/${FILE_NAME}"
HOST_PATH="${BACKUP_DIR}/${FILE_NAME}"

cd "${DEPLOY_DIR}"
mkdir -p "${BACKUP_DIR}"
umask 077

docker compose exec -T api python - "${CONTAINER_PATH}" <<'PY'
import sqlite3
import sys

source = sqlite3.connect("/data/wilson_lab.db")
target = sqlite3.connect(sys.argv[1])
try:
    source.backup(target)
finally:
    target.close()
    source.close()
PY

docker compose cp "api:${CONTAINER_PATH}" "${HOST_PATH}"
docker compose exec -T api rm -f "${CONTAINER_PATH}"
chmod 0600 "${HOST_PATH}"

echo "Backup written to ${HOST_PATH}"
