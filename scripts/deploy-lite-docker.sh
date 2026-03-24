#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/deploy-lite-docker.sh [--project-name NAME] [--yes] [--skip-build] [--skip-data-sync] [--skip-healthcheck] [--services SCOPE] [--backend-mode MODE] [--frontend-mode MODE] [--frontend-image IMAGE]

Interactive deploy helper for the lite docker-compose stack.

Options:
  --project-name NAME   Override docker compose project name.
  --yes                 Use defaults without interactive prompts.
  --skip-build          Legacy shortcut. Equivalent to backend/frontend mode = reuse.
  --skip-data-sync      Do not sync apps/backend/web/data/lite_runtime into the named volume.
  --skip-healthcheck    Do not run HTTP health checks after startup.
  --services SCOPE      Deploy scope: all, backend, frontend.
  --backend-mode MODE   Backend strategy: build, reuse.
  --frontend-mode MODE  Frontend strategy: build, reuse, remote-image.
  --frontend-image IMG  Frontend image used by remote-image mode.
  -h, --help            Show this help.
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

prompt_input() {
  local message="$1"
  local default_value="${2:-}"
  local allow_empty="${3:-false}"
  local prompt_suffix=""
  local reply=""

  if [[ -n "$default_value" ]]; then
    prompt_suffix=" [$default_value]"
  fi

  if [[ "$assume_yes" == "true" ]]; then
    printf '%s\n' "$default_value"
    return 0
  fi

  while true; do
    read -r -p "$message$prompt_suffix: " reply
    reply="${reply:-$default_value}"
    if [[ -n "$reply" || "$allow_empty" == "true" ]]; then
      printf '%s\n' "$reply"
      return 0
    fi
    echo "Value cannot be empty."
  done
}

prompt_secret() {
  local message="$1"
  local reply=""

  if [[ "$assume_yes" == "true" ]]; then
    printf '%s\n' ""
    return 0
  fi

  while true; do
    read -r -s -p "$message: " reply
    echo
    if [[ -n "$reply" ]]; then
      printf '%s\n' "$reply"
      return 0
    fi
    echo "Value cannot be empty."
  done
}

prompt_menu() {
  local prompt="$1"
  local default_value="$2"
  shift 2
  local options=("$@")
  local reply=""
  local index=0
  local default_index=1
  local item=""
  local value=""
  local label=""

  for index in "${!options[@]}"; do
    item="${options[$index]}"
    value="${item%%::*}"
    label="${item#*::}"
    if [[ "$value" == "$default_value" ]]; then
      default_index="$((index + 1))"
    fi
  done

  echo "$prompt" >&2
  for index in "${!options[@]}"; do
    item="${options[$index]}"
    label="${item#*::}"
    echo "  $((index + 1))) $label" >&2
  done

  if [[ "$assume_yes" == "true" ]]; then
    printf '%s\n' "$default_value"
    return 0
  fi

  while true; do
    read -r -p "Choose an option [$default_index]: " reply
    reply="${reply:-$default_index}"
    if [[ "$reply" =~ ^[0-9]+$ ]] && (( reply >= 1 && reply <= ${#options[@]} )); then
      item="${options[$((reply - 1))]}"
      printf '%s\n' "${item%%::*}"
      return 0
    fi
    echo "Please choose a number between 1 and ${#options[@]}."
  done
}

default_project_name() {
  basename "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_.-]+/-/g'
}

compose() {
  docker compose --project-name "$project_name" "${compose_file_args[@]}" "$@"
}

default_registry_from_image() {
  local image_ref="$1"
  local first_segment=""

  if [[ "$image_ref" != */* ]]; then
    return 0
  fi

  first_segment="${image_ref%%/*}"
  if [[ "$first_segment" == "localhost" || "$first_segment" == *.* || "$first_segment" == *:* ]]; then
    printf '%s\n' "$first_segment"
  fi
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

ensure_remote_frontend_login_config() {
  local default_registry=""

  default_registry="$(default_registry_from_image "$frontend_image")"

  if [[ -n "$tcr_registry" || -n "$tcr_username" || -n "$tcr_password" ]]; then
    if [[ -z "$tcr_registry" ]]; then
      tcr_registry="$(prompt_input "TCR registry" "$default_registry")"
    fi
    if [[ -z "$tcr_username" ]]; then
      tcr_username="$(prompt_input "TCR username" "$tcr_username")"
    fi
    if [[ -z "$tcr_password" ]]; then
      tcr_password="$(prompt_secret "TCR password")"
    fi
    return 0
  fi

  if prompt_yes_no "Login to image registry before pulling frontend image?" "Y"; then
    tcr_registry="$(prompt_input "TCR registry" "$default_registry")"
    tcr_username="$(prompt_input "TCR username" "$tcr_username")"
    tcr_password="$(prompt_secret "TCR password")"
  fi
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

validate_services() {
  case "$1" in
    all|backend|frontend)
      ;;
    *)
      echo "Invalid --services value: $1" >&2
      exit 1
      ;;
  esac
}

validate_backend_mode() {
  case "$1" in
    build|reuse)
      ;;
    *)
      echo "Invalid --backend-mode value: $1" >&2
      exit 1
      ;;
  esac
}

validate_frontend_mode() {
  case "$1" in
    build|reuse|remote-image)
      ;;
    *)
      echo "Invalid --frontend-mode value: $1" >&2
      exit 1
      ;;
  esac
}

assume_yes="false"
skip_build="false"
skip_data_sync="false"
skip_healthcheck="false"
project_name=""
services="${DEPLOY_SERVICES:-}"
backend_mode="${BACKEND_DEPLOY_MODE:-}"
frontend_mode="${FRONTEND_DEPLOY_MODE:-}"
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
    --services)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --services" >&2
        usage >&2
        exit 1
      fi
      services="$2"
      shift 2
      ;;
    --backend-mode)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --backend-mode" >&2
        usage >&2
        exit 1
      fi
      backend_mode="$2"
      shift 2
      ;;
    --frontend-mode)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --frontend-mode" >&2
        usage >&2
        exit 1
      fi
      frontend_mode="$2"
      shift 2
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

if [[ ! -f "$compose_file" ]]; then
  echo "Missing compose file: $compose_file" >&2
  exit 1
fi

if [[ "$skip_build" == "true" ]]; then
  if [[ -z "$backend_mode" ]] && [[ "$services" != "frontend" ]]; then
    backend_mode="reuse"
  fi
  if [[ -z "$frontend_mode" ]] && [[ "$services" != "backend" ]]; then
    frontend_mode="reuse"
  fi
fi

if [[ -z "$services" ]]; then
  if [[ -n "$frontend_image" ]]; then
    services="frontend"
  else
    services="all"
  fi
fi

if [[ "$services" == "all" || "$services" == "backend" ]]; then
  backend_mode="${backend_mode:-build}"
fi
if [[ "$services" == "all" || "$services" == "frontend" ]]; then
  if [[ -n "$frontend_image" ]]; then
    frontend_mode="${frontend_mode:-remote-image}"
  else
    frontend_mode="${frontend_mode:-build}"
  fi
fi

validate_services "$services"
if [[ "$services" == "all" || "$services" == "backend" ]]; then
  validate_backend_mode "$backend_mode"
fi
if [[ "$services" == "all" || "$services" == "frontend" ]]; then
  validate_frontend_mode "$frontend_mode"
fi

if [[ "$assume_yes" != "true" ]]; then
  echo "==> deploy menu"
  services="$(prompt_menu \
    "Select deploy scope" \
    "$services" \
    "all::Full stack (backend + frontend)" \
    "frontend::Frontend only" \
    "backend::Backend only")"

  if [[ "$services" == "all" || "$services" == "backend" ]]; then
    backend_mode="${backend_mode:-build}"
    backend_mode="$(prompt_menu \
      "Select backend deploy mode" \
      "$backend_mode" \
      "build::Build backend locally before deploy" \
      "reuse::Reuse current local backend image")"
  else
    backend_mode=""
  fi

  if [[ "$services" == "all" || "$services" == "frontend" ]]; then
    frontend_mode="${frontend_mode:-build}"
    frontend_mode="$(prompt_menu \
      "Select frontend deploy mode" \
      "$frontend_mode" \
      "build::Build frontend locally before deploy" \
      "reuse::Reuse current local frontend image" \
      "remote-image::Pull remote frontend image")"
  else
    frontend_mode=""
  fi
  echo
fi

if [[ "$services" == "all" || "$services" == "frontend" ]] && [[ "$frontend_mode" == "remote-image" ]]; then
  if [[ -z "$frontend_image" ]]; then
    frontend_image="$(prompt_input "Remote frontend image" "$frontend_image")"
  fi
  if [[ -z "$frontend_image" ]]; then
    echo "FRONTEND_IMAGE is required when frontend mode is remote-image." >&2
    exit 1
  fi
  if [[ ! -f "$server_compose_file" ]]; then
    echo "Missing server compose file: $server_compose_file" >&2
    exit 1
  fi
  ensure_remote_frontend_login_config
  export FRONTEND_IMAGE="$frontend_image"
  compose_file_args+=(--file "$server_compose_file")
fi

if [[ -z "$project_name" ]]; then
  project_name="${COMPOSE_PROJECT_NAME:-$(default_project_name "$repo_root")}"
fi

runtime_volume="${project_name}_backend_runtime"
logs_volume="${project_name}_backend_logs"
mkdir -p "$logs_dir"

services_to_up=()
build_services=()
pull_services=()

if [[ "$services" == "all" || "$services" == "backend" ]]; then
  services_to_up+=("backend")
  if [[ "$backend_mode" == "build" ]]; then
    build_services+=("backend")
  fi
fi

if [[ "$services" == "all" || "$services" == "frontend" ]]; then
  services_to_up+=("frontend")
  case "$frontend_mode" in
    build)
      build_services+=("frontend")
      ;;
    remote-image)
      pull_services+=("frontend")
      ;;
  esac
fi

echo "==> lite docker deploy helper"
echo "repo root: $repo_root"
echo "compose files: ${compose_file_args[*]}"
echo "project name: $project_name"
echo "deploy scope: $services"
echo "backend mode: ${backend_mode:-n/a}"
echo "frontend mode: ${frontend_mode:-n/a}"
echo "runtime dir: $runtime_dir"
echo "runtime volume: $runtime_volume"
echo "logs volume: $logs_volume"
echo "backend health url: $backend_health_url"
echo "frontend health url: $frontend_health_url"
echo "frontend proxy health url: $frontend_proxy_health_url"
if [[ "$frontend_mode" == "remote-image" ]] && [[ -n "$frontend_image" ]]; then
  echo "frontend image: $frontend_image"
fi
echo
echo "Note: current compose uses named volumes."
echo "Files under apps/backend/web/data/lite_runtime do NOT auto-map into the container."
echo "If you want the checked-out runtime data to be used, this script needs to sync it into the named volume first."
echo

sync_data="false"
if [[ "$services" != "frontend" ]] && [[ "$skip_data_sync" != "true" ]] && [[ -d "$runtime_dir" ]] && find "$runtime_dir" -mindepth 1 -print -quit | grep -q .; then
  if prompt_yes_no "Sync local lite_runtime into docker volume before startup?" "Y"; then
    sync_data="true"
  fi
fi

run_down_first="false"
if [[ "$services" == "all" ]]; then
  if prompt_yes_no "Run docker compose down first?" "Y"; then
    run_down_first="true"
  fi
else
  echo "Skip full compose down because partial deploy was selected."
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

if [[ "${#build_services[@]}" -gt 0 ]]; then
  compose build "${build_services[@]}"
fi

if [[ "${#pull_services[@]}" -gt 0 ]]; then
  docker_login_if_needed
  compose pull "${pull_services[@]}"
fi

compose up -d --no-build "${services_to_up[@]}"

echo
compose ps

if [[ "$show_logs" == "true" ]]; then
  echo
  compose logs --tail 80 "${services_to_up[@]}"
fi

if [[ "$run_healthcheck" == "true" ]]; then
  echo
  echo "==> health checks"
  if [[ "$services" == "all" || "$services" == "backend" ]]; then
    check_service_running backend
    wait_for_http "backend docs" "$backend_health_url" "$health_timeout"
  fi
  if [[ "$services" == "all" || "$services" == "frontend" ]]; then
    check_service_running frontend
    wait_for_http "frontend index" "$frontend_health_url" "$health_timeout"
  fi
  if [[ "$services" == "all" ]]; then
    wait_for_http "frontend proxy to backend" "$frontend_proxy_health_url" "$health_timeout"
  fi
fi
