#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/bootstrap-worktree.sh [--skip-backend] [--skip-frontend]

Initialize only the current git worktree:
- backend: uv sync --python 3.11 --frozen --group dev
- frontend: pnpm install --frozen-lockfile --prefer-offline

This script is safe to run from any subdirectory inside the current worktree.
It reuses package-manager caches when available, but does not try to share
node_modules or .venv across different worktrees.
EOF
}

require_cmd() {
  local name="$1"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "Missing required command: $name" >&2
    exit 1
  fi
}

run_backend=1
run_frontend=1

for arg in "$@"; do
  case "$arg" in
    --skip-backend)
      run_backend=0
      ;;
    --skip-frontend)
      run_frontend=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      usage >&2
      exit 1
      ;;
  esac
done

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

require_cmd git

echo "==> bootstrap current worktree"
echo "repo root: $repo_root"

mkdir -p apps/backend/weblogs
mkdir -p apps/backend/web/data/lite_runtime

if [[ "$run_backend" -eq 1 ]]; then
  require_cmd uv
  echo "==> sync backend dependencies with uv (Python 3.11)"
  uv sync --python 3.11 --frozen --group dev
fi

if [[ "$run_frontend" -eq 1 ]]; then
  require_cmd pnpm
  echo "==> sync frontend dependencies with pnpm workspace"
  pnpm install --frozen-lockfile --prefer-offline
fi

cat <<'EOF'
==> done

Notes:
- This script only initializes the current worktree.
- Backend runtime uses the current worktree's uv-managed .venv.
- Shared package-manager caches are fine, but do not manually share .venv or node_modules across worktrees.
- Recommended shell defaults after bootstrap:
  export SNOW_APP_STATUS=lite
  source .venv/bin/activate
EOF
