#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SECRET_DIR="${DEPLOY_DIR}/secrets"
API_UID=10001
API_GID=10001

command -v openssl >/dev/null 2>&1 || {
  echo "openssl is required" >&2
  exit 1
}

if [[ ${EUID} -eq 0 ]]; then
  ROOT=()
else
  command -v sudo >/dev/null 2>&1 || {
    echo "sudo is required to assign secret files to the API container identity" >&2
    exit 1
  }
  ROOT=(sudo)
fi

"${ROOT[@]}" mkdir -p "${SECRET_DIR}"

install_secret() {
  local name="$1"
  local bytes="$2"
  local target="${SECRET_DIR}/${name}"

  if "${ROOT[@]}" test -s "${target}"; then
    echo "Keeping existing ${name}"
    return
  fi

  local temporary
  temporary="$(mktemp)"
  trap 'rm -f "${temporary:-}"' RETURN
  umask 077
  openssl rand -base64 "${bytes}" | tr -d '\n' > "${temporary}"
  "${ROOT[@]}" install -o "${API_UID}" -g "${API_GID}" -m 0400 "${temporary}" "${target}"
  rm -f "${temporary}"
  trap - RETURN
  echo "Generated ${name}"
}

install_secret jwt_secret 48
install_secret viewer_password 24
install_secret admin_password 24

echo "Secrets are installed for container UID/GID ${API_UID}:${API_GID}."
echo "Use: bash deploy/scripts/show-credentials.sh"
