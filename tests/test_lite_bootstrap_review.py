import os
import pathlib
import subprocess
import sys
import textwrap
from types import SimpleNamespace

import pytest

from web.common.cache import cache
from web.scheduler import _resolve_job_id


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
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


def test_scheduler_job_id_resolution_falls_back_when_cache_is_disabled() -> None:
    cache.reset()
    event = SimpleNamespace(job_id="demo-job")

    assert _resolve_job_id(event) == "demo-job"
