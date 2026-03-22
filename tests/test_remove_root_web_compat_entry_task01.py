from __future__ import annotations

from pathlib import Path

import web


BACKEND_WORKSPACE = Path(__file__).resolve().parents[1] / "apps" / "backend"


def test_repo_root_import_bootstraps_web_from_backend_workspace():
    assert Path(web.__file__).as_posix().startswith(BACKEND_WORKSPACE.as_posix())
