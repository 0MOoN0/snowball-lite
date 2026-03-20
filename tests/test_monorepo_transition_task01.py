from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = REPO_ROOT / "apps" / "frontend"
LEGACY_ROOT = REPO_ROOT / "snow_view"


def test_frontend_workspace_is_trimmed_for_monorepo_intake():
    # node_modules 和 dist-* 属于本地运行产物，后续 task 会通过根 .gitignore 约束；
    # 这里继续卡住“独立仓库残留物”和不该再回来的旧部署文件。
    forbidden_paths = [
        FRONTEND_ROOT / ".git",
        FRONTEND_ROOT / ".github",
        FRONTEND_ROOT / ".husky",
        FRONTEND_ROOT / ".vscode",
        FRONTEND_ROOT / ".cursor",
        FRONTEND_ROOT / ".trae",
        FRONTEND_ROOT / "package-lock.json",
        FRONTEND_ROOT / "Dockerfile",
        FRONTEND_ROOT / "docker-compose.yml",
        FRONTEND_ROOT / "nginx_config",
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in forbidden_paths if path.exists()]

    assert missing == [], f"forbidden legacy paths still exist: {missing}"
    assert not LEGACY_ROOT.exists(), "legacy snow_view path should be removed after workspace bootstrap"


def test_frontend_package_is_workspace_ready():
    package_json_path = FRONTEND_ROOT / "package.json"
    package = json.loads(package_json_path.read_text(encoding="utf-8"))

    assert package["private"] is True
    assert "repository" not in package
    assert "bugs" not in package
    assert "homepage" not in package
    assert "prepare" not in package["scripts"]
    assert "lint:lint-staged" not in package["scripts"]
    assert "npm:check" not in package["scripts"]
    assert package["scripts"]["build:dev"] == "pnpm run ts:check && vite build --mode dev"
    assert package["scripts"]["build:test"] == "pnpm run ts:check && vite build --mode test"
    assert package["scripts"]["clean"] == "pnpm exec rimraf node_modules"
    assert package["scripts"]["clean:cache"] == "pnpm exec rimraf node_modules/.cache"


def test_root_workspace_registers_frontend_package():
    workspace_path = REPO_ROOT / "pnpm-workspace.yaml"
    readme_path = REPO_ROOT / "README.md"
    lockfile_path = REPO_ROOT / "pnpm-lock.yaml"

    workspace_text = workspace_path.read_text(encoding="utf-8")
    readme_text = readme_path.read_text(encoding="utf-8")
    lockfile_text = lockfile_path.read_text(encoding="utf-8")

    assert "apps/frontend" in workspace_text
    assert "snow_view" not in workspace_text
    assert "apps/frontend" in readme_text
    assert "pnpm install" in readme_text
    assert "apps/frontend:" in lockfile_text


def test_root_gitignore_covers_frontend_workspace_artifacts():
    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "node_modules/" in gitignore_text
    assert "apps/frontend/dist/" in gitignore_text
    assert "apps/frontend/dist-dev/" in gitignore_text
    assert "apps/frontend/dist-pro/" in gitignore_text
    assert "apps/frontend/dist-test/" in gitignore_text
