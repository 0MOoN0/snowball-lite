from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_WORKSPACE = REPO_ROOT / "apps" / "backend"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_backend_workspace_bridge_and_docs_path_remain_available():
    assert BACKEND_WORKSPACE.is_dir()
    assert (BACKEND_WORKSPACE / "web").is_dir()
    assert not (BACKEND_WORKSPACE / "web").is_symlink()
    assert (BACKEND_WORKSPACE / "xalpha").is_symlink()
    assert (REPO_ROOT / "web").is_symlink()
    assert (REPO_ROOT / "web" / "docs").is_dir()
    assert (REPO_ROOT / "web" / "docs" / "review" / "monorepo_transition").is_dir()


def test_backend_workspace_can_import_web_and_xalpha_from_apps_backend(tmp_path: Path):
    db_path = tmp_path / "task04_backend.db"
    cache_dir = tmp_path / "task04_cache"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            textwrap.dedent(
                f"""
                import json
                import os
                from pathlib import Path

                os.environ["LITE_DB_PATH"] = str(Path({str(db_path)!r}))
                os.environ["LITE_XALPHA_CACHE_DIR"] = str(Path({str(cache_dir)!r}))
                os.environ["LITE_XALPHA_CACHE_BACKEND"] = "csv"

                import web.lite_application as lite_application
                import xalpha

                print(
                    json.dumps(
                        {{
                            "config": lite_application.app.config["_config_name"],
                            "xalpha_path": xalpha.__file__,
                            "docs_available": Path("web/docs").is_dir(),
                        }}
                    )
                )
                """
            ),
            ],
        cwd=BACKEND_WORKSPACE,
        text=True,
        capture_output=True,
        env=os.environ.copy(),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["config"] == "lite"
    assert payload["docs_available"] is True
    assert payload["xalpha_path"]


def test_backend_workspace_commands_are_retargeted():
    root_readme = _read_text(REPO_ROOT / "README.md")
    env_guide = _read_text(REPO_ROOT / "web" / "docs" / "环境变量配置指南.md")
    dockerfile = _read_text(REPO_ROOT / "Dockerfile")
    compose = _read_text(REPO_ROOT / "docker-compose.yml")
    backend_readme = _read_text(BACKEND_WORKSPACE / "README.md")

    assert "cd apps/backend" in root_readme
    assert "cd apps/backend && python -m web.lite_application" in root_readme
    assert "cd apps/backend && SNOW_APP_STATUS=dev python -m web.application" in root_readme
    assert "gunicorn -c web/gunicorn.config.py web.application:app" in root_readme
    assert "cd apps/backend && uv run --no-dev python -m web.lite_application" in env_guide
    assert "WORKDIR /app/apps/backend" in dockerfile
    assert "FLASK_APP=web.application:app" in compose
    assert "/app/apps/backend/weblogs" in compose
    assert "cd apps/backend" in backend_readme
