#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/deploy-lite-docker.sh [--project-name NAME] [--yes] [--skip-build] [--skip-data-sync] [--skip-healthcheck] [--frontend-image IMAGE]

Interactive deploy helper for the lite docker-compose stack.

Options:
  --project-name NAME  Override docker compose project name.
  --yes                Use defaults without interactive prompts.
  --skip-build         Skip image rebuild and run plain `docker compose up -d`.
  --skip-data-sync     Do not sync apps/backend/web/data/lite_runtime into the named volume.
  --skip-healthcheck   Do not run HTTP health checks after startup.
  --frontend-image IMG Pull and deploy frontend from a remote image instead of local build.
  -h, --help           Show this help.
EOF
}

require_cmd() {
  local name="$1"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "Missing required command: $name" >&2
    exit 1
  fi
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

prompt_yes_no() {
  local message="$1"
  local default_answer="${2:-Y}"
  local prompt_hint="[Y/n]"
  local reply=""

  if [[ "$default_answer" == "N" ]]; then
    prompt_hint="[y/N]"
  fi

  if [[ "$assume_yes" == "true" ]]; then
    [[ "$default_answer" == "Y" ]]
    return
  fi

  while true; do
    read -r -p "$message $prompt_hint " reply
    reply="${reply:-$default_answer}"
    case "$reply" in
      Y|y)
        return 0
        ;;
      N|n)
        return 1
        ;;
      *)
        echo "Please answer y or n."
        ;;
    esac
  done
}

default_project_name() {
  basename "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_.-]+/-/g'
}

compose() {
  docker compose --project-name "$project_name" "${compose_file_args[@]}" "$@"
}

docker_login_if_needed() {
  if [[ -z "${tcr_registry:-}" && -z "${tcr_username:-}" && -z "${tcr_password:-}" ]]; then
    return 0
  fi

  if [[ -z "${tcr_registry:-}" || -z "${tcr_username:-}" || -z "${tcr_password:-}" ]]; then
    echo "TCR_REGISTRY, TCR_USERNAME and TCR_PASSWORD must be set together when using remote frontend image mode." >&2
    exit 1
  fi

  printf '%s\n' "$tcr_password" | docker login "$tcr_registry" --username "$tcr_username" --password-stdin
}

volume_has_files() {
  local volume_name="$1"

  docker run --rm \
    -v "$volume_name:/target" \
    alpine:3.20 \
    sh -c 'find /target -mindepth 1 -print -quit' 2>/dev/null | grep -q .
}

sync_runtime_data_to_volume() {
  local volume_name="$1"
  local source_dir="$2"

  docker volume create "$volume_name" >/dev/null

  docker run --rm \
    -v "$volume_name:/target" \
    -v "$source_dir:/source:ro" \
    alpine:3.20 \
    sh -c '
      mkdir -p /target
      find /target -mindepth 1 -maxdepth 1 -exec rm -rf {} +
      cp -a /source/. /target/
    '
}

http_get_status() {
  local url="$1"
  local status=""

  if has_cmd curl; then
    status="$(curl -sS -L -o /dev/null -w '%{http_code}' "$url" || true)"
  elif has_cmd wget; then
    status="$(wget -S -O /dev/null "$url" 2>&1 | awk '/^  HTTP\\// {code=$2} END {print code}')"
  else
    echo ""
    return 0
  fi

  echo "$status"
}

wait_for_http() {
  local name="$1"
  local url="$2"
  local timeout_seconds="${3:-120}"
  local interval_seconds=2
  local start_ts
  local now_ts
  local status=""

  start_ts="$(date +%s)"

  while true; do
    status="$(http_get_status "$url")"
    if [[ "$status" =~ ^2[0-9][0-9]$ || "$status" =~ ^3[0-9][0-9]$ ]]; then
      echo "[ok] $name -> $url ($status)"
      return 0
    fi

    now_ts="$(date +%s)"
    if (( now_ts - start_ts >= timeout_seconds )); then
      echo "[fail] $name -> $url (last status: ${status:-unavailable})" >&2
      return 1
    fi

    sleep "$interval_seconds"
  done
}

check_service_running() {
  local service_name="$1"
  local container_id=""
  local state

  container_id="$(compose ps -q "$service_name" 2>/dev/null | head -n 1)"
  if [[ -z "$container_id" ]]; then
    echo "[fail] service $service_name container not found" >&2
    return 1
  fi

  state="$(docker inspect -f '{{.State.Status}}' "$container_id" 2>/dev/null || true)"

  if [[ "$state" == "running" ]]; then
    echo "[ok] service $service_name is running"
    return 0
  fi

  echo "[fail] service $service_name state: ${state:-unknown}" >&2
  return 1
}

assume_yes="false"
skip_build="false"
skip_data_sync="false"
skip_healthcheck="false"
project_name=""
frontend_image="${FRONTEND_IMAGE:-}"
tcr_registry="${TCR_REGISTRY:-}"
tcr_username="${TCR_USERNAME:-}"
tcr_password="${TCR_PASSWORD:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-name)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --project-name" >&2
        usage >&2
        exit 1
      fi
      project_name="$2"
      shift 2
      ;;
    --yes)
      assume_yes="true"
      shift
      ;;
    --skip-build)
      skip_build="true"
      shift
      ;;
    --skip-data-sync)
      skip_data_sync="true"
      shift
      ;;
    --skip-healthcheck)
      skip_healthcheck="true"
      shift
      ;;
    --frontend-image)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --frontend-image" >&2
        usage >&2
        exit 1
      fi
      frontend_image="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

require_cmd git
require_cmd docker

repo_root="$(git rev-parse --show-toplevel)"
compose_file="$repo_root/docker-compose.yml"
server_compose_file="$repo_root/docker-compose.server.yml"
runtime_dir="$repo_root/apps/backend/web/data/lite_runtime"
logs_dir="$repo_root/apps/backend/weblogs"
backend_health_url="${BACKEND_HEALTH_URL:-http://127.0.0.1:5001/docs}"
frontend_health_url="${FRONTEND_HEALTH_URL:-http://127.0.0.1:8080}"
frontend_proxy_health_url="${FRONTEND_PROXY_HEALTH_URL:-http://127.0.0.1:8080/dev/docs}"
health_timeout="${HEALTHCHECK_TIMEOUT_SECONDS:-120}"
compose_file_args=(--file "$compose_file")
deploy_mode="local-build"

if [[ ! -f "$compose_file" ]]; then
  echo "Missing compose file: $compose_file" >&2
  exit 1
fi

if [[ -n "$frontend_image" ]]; then
  if [[ ! -f "$server_compose_file" ]]; then
    echo "Missing server compose file: $server_compose_file" >&2
    exit 1
  fi
  export FRONTEND_IMAGE="$frontend_image"
  compose_file_args+=(--file "$server_compose_file")
  deploy_mode="remote-frontend-image"
fi

if [[ -z "$project_name" ]]; then
  project_name="${COMPOSE_PROJECT_NAME:-$(default_project_name "$repo_root")}"
fi

runtime_volume="${project_name}_backend_runtime"
logs_volume="${project_name}_backend_logs"

mkdir -p "$logs_dir"

echo "==> lite docker deploy helper"
echo "repo root: $repo_root"
echo "compose files: ${compose_file_args[*]}"
echo "deploy mode: $deploy_mode"
echo "project name: $project_name"
echo "runtime dir: $runtime_dir"
echo "runtime volume: $runtime_volume"
echo "logs volume: $logs_volume"
echo "backend health url: $backend_health_url"
echo "frontend health url: $frontend_health_url"
echo "frontend proxy health url: $frontend_proxy_health_url"
if [[ -n "$frontend_image" ]]; then
  echo "frontend image: $frontend_image"
fi
echo
echo "Note: current compose uses named volumes."
echo "Files under apps/backend/web/data/lite_runtime do NOT auto-map into the container."
echo "If you want the checked-out runtime data to be used, this script needs to sync it into the named volume first."
echo

sync_data="false"
if [[ "$skip_data_sync" != "true" ]] && [[ -d "$runtime_dir" ]] && find "$runtime_dir" -mindepth 1 -print -quit | grep -q .; then
  if prompt_yes_no "Sync local lite_runtime into docker volume before startup?" "Y"; then
    sync_data="true"
  fi
fi

run_down_first="false"
if prompt_yes_no "Run docker compose down first?" "Y"; then
  run_down_first="true"
fi

show_logs="false"
if prompt_yes_no "Show startup logs after deploy?" "N"; then
  show_logs="true"
fi

run_healthcheck="false"
if [[ "$skip_healthcheck" != "true" ]] && ( has_cmd curl || has_cmd wget ); then
  if prompt_yes_no "Run HTTP health checks after deploy?" "Y"; then
    run_healthcheck="true"
  fi
elif [[ "$skip_healthcheck" != "true" ]]; then
  echo "Skip health checks because neither curl nor wget is available."
fi

if [[ "$run_down_first" == "true" ]]; then
  compose down
fi

if [[ "$sync_data" == "true" ]]; then
  if volume_has_files "$runtime_volume"; then
    if prompt_yes_no "Runtime volume already has files. Overwrite with local lite_runtime?" "N"; then
      sync_runtime_data_to_volume "$runtime_volume" "$runtime_dir"
      echo "Synced runtime data into $runtime_volume"
    else
      echo "Skipped runtime data sync."
    fi
  else
    sync_runtime_data_to_volume "$runtime_volume" "$runtime_dir"
    echo "Synced runtime data into $runtime_volume"
  fi
fi

if [[ -n "$frontend_image" ]]; then
  docker_login_if_needed
  compose pull frontend
  compose up -d frontend
elif [[ "$skip_build" == "true" ]]; then
  compose up -d
else
  compose up -d --build
fi

echo
compose ps

if [[ "$show_logs" == "true" ]]; then
  echo
  compose logs --tail 80 backend frontend
fi

if [[ "$run_healthcheck" == "true" ]]; then
  echo
  echo "==> health checks"
  check_service_running backend
  check_service_running frontend
  wait_for_http "backend docs" "$backend_health_url" "$health_timeout"
  wait_for_http "frontend index" "$frontend_health_url" "$health_timeout"
  wait_for_http "frontend proxy to backend" "$frontend_proxy_health_url" "$health_timeout"
fi
