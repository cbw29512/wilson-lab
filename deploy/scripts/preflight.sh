#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${DEPLOY_DIR}/.env"
SECRET_DIR="${DEPLOY_DIR}/secrets"

command -v docker >/dev/null 2>&1 || {
  echo "Docker is not installed" >&2
  exit 1
}
docker compose version >/dev/null
[[ -S /var/run/docker.sock ]] || {
  echo "/var/run/docker.sock is unavailable" >&2
  exit 1
}
[[ -f "${ENV_FILE}" ]] || {
  echo "Copy deploy/.env.example to deploy/.env first" >&2
  exit 1
}

set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

[[ -n "${API_DOMAIN:-}" && "${API_DOMAIN}" != "api.example.com" ]] || {
  echo "Set a real API_DOMAIN in deploy/.env" >&2
  exit 1
}

ACTUAL_DOCKER_GID="$(stat -c '%g' /var/run/docker.sock)"
[[ "${DOCKER_GID:-}" == "${ACTUAL_DOCKER_GID}" ]] || {
  echo "DOCKER_GID must be ${ACTUAL_DOCKER_GID}" >&2
  exit 1
}

for secret in jwt_secret viewer_password admin_password; do
  [[ -s "${SECRET_DIR}/${secret}" ]] || {
    echo "Missing secret: ${SECRET_DIR}/${secret}" >&2
    exit 1
  }
done

cd "${DEPLOY_DIR}"
docker compose config --quiet
docker run --rm \
  -e API_DOMAIN="${API_DOMAIN}" \
  -v "${DEPLOY_DIR}/Caddyfile:/etc/caddy/Caddyfile:ro" \
  caddy:2.11.4-alpine \
  caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile

echo "Preflight passed for ${API_DOMAIN}."
