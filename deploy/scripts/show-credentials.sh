#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SECRET_DIR="${DEPLOY_DIR}/secrets"
ENV_FILE="${DEPLOY_DIR}/.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing deploy/.env" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

read_secret() {
  local path="$1"
  if [[ ${EUID} -eq 0 ]]; then
    cat "${path}"
  else
    sudo cat "${path}"
  fi
}

printf 'Viewer username: %s\n' "${VIEWER_USERNAME:-viewer}"
printf 'Viewer password: '
read_secret "${SECRET_DIR}/viewer_password"
printf '\nAdministrator username: %s\n' "${ADMIN_USERNAME:-admin}"
printf 'Administrator password: '
read_secret "${SECRET_DIR}/admin_password"
printf '\n'
