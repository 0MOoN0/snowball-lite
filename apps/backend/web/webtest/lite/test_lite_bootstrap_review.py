import os
import pathlib
import subprocess
import sys
import textwrap
from types import SimpleNamespace

import pytest

from web.common.cache import cache
from web.common.utils.backend_paths import get_repo_root
from web.lite_bootstrap import get_lite_head_revision
from web.scheduler import _resolve_job_id


REPO_ROOT = get_repo_root()
pytestmark = pytest.mark.local


def _run_python_with_blocked_imports(tmp_path: pathlib.Path, blocked_modules: set[str], code: str) -> subprocess.CompletedProcess[str]:
    sitecustomize = tmp_path / "sitecustomize.py"
    blocked_repr = ", ".join(repr(name) for name in sorted(blocked_modules))
    sitecustomize.write_text(
        textwrap.dedent(
            f"""
            import importlib.abc
            import sys

            BLOCKED = {{{blocked_repr}}}


            class _BlockingFinder(importlib.abc.MetaPathFinder):
                def find_spec(self, fullname, path=None, target=None):
                    if any(fullname == name or fullname.startswith(name + ".") for name in BLOCKED):
                        raise ModuleNotFoundError(f"blocked import: {{fullname}}")
                    return None


            sys.meta_path.insert(0, _BlockingFinder())
            """
        ),
        encoding="utf-8",
    )

    env = os.environ.copy()
    pythonpath = [str(tmp_path), str(REPO_ROOT)]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)

    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
    )


def test_lite_bootstrap_does_not_require_optional_infra_packages(tmp_path: pathlib.Path) -> None:
    result = _run_python_with_blocked_imports(
        tmp_path=tmp_path,
        blocked_modules={
            "apscheduler",
            "dramatiq",
            "flask_apscheduler",
            "flask_profiler",
            "redis",
        },
        code="from web import create_app\ncreate_app('lite')\nprint('LITE_OK')",
    )

    assert result.returncode == 0, result.stderr
    assert "LITE_OK" in result.stdout


def test_lite_bootstrap_survives_blocked_mysql_and_optional_infra_packages(tmp_path: pathlib.Path) -> None:
    db_path = tmp_path / "snowball_lite.db"
    cache_dir = tmp_path / "lite_xalpha_cache"

    result = _run_python_with_blocked_imports(
        tmp_path=tmp_path,
        blocked_modules={
            "MySQLdb",
            "apscheduler",
            "dramatiq",
            "flask_apscheduler",
            "flask_profiler",
            "mysql",
            "pymysql",
            "redis",
        },
        code=textwrap.dedent(
            f"""
            import json
            import os
            from pathlib import Path

            from sqlalchemy import inspect, text

            os.environ["LITE_DB_PATH"] = str(Path({str(db_path)!r}))
            os.environ["LITE_XALPHA_CACHE_DIR"] = str(Path({str(cache_dir)!r}))
            os.environ["LITE_XALPHA_CACHE_BACKEND"] = "csv"

            from web import create_app
            from web.lite_bootstrap import bootstrap_lite_database, get_lite_head_revision
            from web.models import db

            app = create_app("lite")

            with app.app_context():
                bootstrap_lite_database(app)
                engine = db.engines["snowball"]
                table_names = set(inspect(engine).get_table_names())

                with engine.connect() as conn:
                    version = conn.execute(
                        text("SELECT version_num FROM alembic_version")
                    ).scalar()
                    foreign_keys = conn.execute(text("PRAGMA foreign_keys")).scalar()
                    journal_mode = conn.execute(text("PRAGMA journal_mode")).scalar()

                assert version == get_lite_head_revision()
                assert "tb_asset" in table_names
                assert "tb_record" in table_names
                assert "tb_apscheduler_log" in table_names
                assert foreign_keys == 1
                assert str(journal_mode).lower() == "wal"
                print(
                    json.dumps(
                        {{
                            "table_count": len(table_names),
                            "version": version,
                            "foreign_keys": foreign_keys,
                            "journal_mode": journal_mode,
                        }}
                    )
                )

            print("LITE_BOOTSTRAP_OK")
            """
        ),
    )

    assert result.returncode == 0, result.stderr
    assert "LITE_BOOTSTRAP_OK" in result.stdout
    assert f'"version": "{get_lite_head_revision()}"' in result.stdout


def test_lite_application_bootstraps_database_when_imported(tmp_path: pathlib.Path) -> None:
    db_path = tmp_path / "lite_app_entry.db"
    cache_dir = tmp_path / "lite_app_entry_cache"

    result = _run_python_with_blocked_imports(
        tmp_path=tmp_path,
        blocked_modules={
            "MySQLdb",
            "apscheduler",
            "dramatiq",
            "flask_apscheduler",
            "flask_profiler",
            "mysql",
            "pymysql",
            "redis",
        },
        code=textwrap.dedent(
            f"""
            import json
            import os
            from pathlib import Path

            from sqlalchemy import inspect, text

            os.environ["LITE_DB_PATH"] = str(Path({str(db_path)!r}))
            os.environ["LITE_XALPHA_CACHE_DIR"] = str(Path({str(cache_dir)!r}))
            os.environ["LITE_XALPHA_CACHE_BACKEND"] = "csv"

            import web.lite_application as lite_application
            from web.models import db

            engine = db.engines["snowball"]
            table_names = set(inspect(engine).get_table_names())

            with engine.connect() as conn:
                version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()

            assert lite_application.app.config["_config_name"] == "lite"
            from web.lite_bootstrap import get_lite_head_revision

            assert version == get_lite_head_revision()
            assert "tb_asset" in table_names
            assert "tb_record" in table_names
            assert "tb_apscheduler_log" in table_names
            print(json.dumps({{"version": version, "table_count": len(table_names)}}))
            print("LITE_APPLICATION_OK")
            """
        ),
    )

    assert result.returncode == 0, result.stderr
    assert "LITE_APPLICATION_OK" in result.stdout
    assert f'"version": "{get_lite_head_revision()}"' in result.stdout


def test_lite_gunicorn_check_config_passes(tmp_path: pathlib.Path) -> None:
    pytest.importorskip("gunicorn")

    db_path = tmp_path / "lite_gunicorn.db"
    cache_sqlite_path = tmp_path / "lite_gunicorn_cache.db"
    env = os.environ.copy()
    pythonpath = [str(REPO_ROOT)]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])

    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    env["LITE_DB_PATH"] = str(db_path)
    env["LITE_XALPHA_CACHE_BACKEND"] = "sql"
    env["LITE_XALPHA_CACHE_SQLITE_PATH"] = str(cache_sqlite_path)
    env["LITE_ENABLE_XALPHA_SQL_CACHE"] = "true"
    env["LITE_FLASK_PORT"] = "5002"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gunicorn.app.wsgiapp",
            "--check-config",
            "-c",
            "apps/backend/web/gunicorn_lite.config.py",
            "web.lite_application:app",
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout


def test_scheduler_job_id_resolution_falls_back_when_cache_is_disabled() -> None:
    cache.reset()
    event = SimpleNamespace(job_id="demo-job")

    assert _resolve_job_id(event) == "demo-job"
