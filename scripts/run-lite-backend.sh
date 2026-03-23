#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run-lite-backend.sh [--runner gunicorn|python|uv]

Start the lite backend with platform-aware defaults.

- Linux is the primary runtime and keeps Gunicorn + gevent.
- Darwin is treated as local compatibility mode.
- The script is safe to run from any subdirectory inside the current worktree.

Defaults:
- runner: gunicorn
- SNOW_APP_STATUS=lite
- LITE_DB_PATH=apps/backend/web/data/lite_runtime/snowball_lite.db
- LITE_XALPHA_CACHE_SQLITE_PATH=apps/backend/web/data/lite_runtime/lite_xalpha_cache/lite_xalpha_cache.db
EOF
}

require_cmd() {
  local name="$1"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "Missing required command: $name" >&2
    exit 1
  fi
}

require_exec() {
  local path="$1"
  if [[ ! -x "$path" ]]; then
    echo "Missing executable: $path" >&2
    exit 1
  fi
}

runner="gunicorn"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runner)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --runner" >&2
        usage >&2
        exit 1
      fi
      runner="$2"
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

case "$runner" in
  gunicorn|python|uv)
    ;;
  *)
    echo "Unsupported runner: $runner" >&2
    usage >&2
    exit 1
    ;;
esac

require_cmd git
repo_root="$(git rev-parse --show-toplevel)"
backend_root="$repo_root/apps/backend"
lite_runtime_dir="$backend_root/web/data/lite_runtime"

mkdir -p "$backend_root/weblogs"
mkdir -p "$lite_runtime_dir"

export SNOW_APP_STATUS="${SNOW_APP_STATUS:-lite}"
export LITE_DB_PATH="${LITE_DB_PATH:-$lite_runtime_dir/snowball_lite.db}"
export LITE_XALPHA_CACHE_BACKEND="${LITE_XALPHA_CACHE_BACKEND:-sql}"
export LITE_ENABLE_XALPHA_SQL_CACHE="${LITE_ENABLE_XALPHA_SQL_CACHE:-true}"
export LITE_XALPHA_CACHE_SQLITE_PATH="${LITE_XALPHA_CACHE_SQLITE_PATH:-$lite_runtime_dir/lite_xalpha_cache/lite_xalpha_cache.db}"

platform="$(uname -s)"
platform_note="Linux/mainline mode: Gunicorn request worker uses gevent."

if [[ "$platform" == "Darwin" ]]; then
  export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
  platform_note="Darwin compatibility mode: pre-export fork safety env and let Gunicorn fall back to sync request worker."
fi

echo "==> lite backend launcher"
echo "repo root: $repo_root"
echo "backend root: $backend_root"
echo "platform: $platform"
echo "runner: $runner"
echo "mode: $platform_note"
echo "LITE_DB_PATH: $LITE_DB_PATH"
echo "LITE_XALPHA_CACHE_SQLITE_PATH: $LITE_XALPHA_CACHE_SQLITE_PATH"

cd "$backend_root"

case "$runner" in
  gunicorn)
    require_exec "$repo_root/.venv/bin/gunicorn"
    exec "$repo_root/.venv/bin/gunicorn" -c web/gunicorn_lite.config.py web.lite_application:app
    ;;
  python)
    require_exec "$repo_root/.venv/bin/python"
    exec "$repo_root/.venv/bin/python" -m web.lite_application
    ;;
  uv)
    require_cmd uv
    exec uv run --no-dev python -m web.lite_application
    ;;
esac
