from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
BACKEND_WORKSPACE = REPO_ROOT / "apps" / "backend" / "web"


def test_docs_root_has_long_term_entry_points():
    expected_files = [
        DOCS_ROOT / "README.md",
        DOCS_ROOT / "architecture" / "README.md",
        DOCS_ROOT / "backend" / "README.md",
        DOCS_ROOT / "frontend" / "README.md",
        DOCS_ROOT / "xalpha" / "README.md",
        DOCS_ROOT / "adr" / "README.md",
        DOCS_ROOT / "ops" / "README.md",
    ]

    missing = [str(path.relative_to(REPO_ROOT)) for path in expected_files if not path.exists()]
    assert missing == [], f"docs entry points are missing: {missing}"


def test_root_readme_points_to_docs_boundaries():
    readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "[docs/README.md](docs/README.md)" in readme_text
    assert "[docs/](docs)" in readme_text
    assert "[apps/backend/web/docs/task/](apps/backend/web/docs/task)" in readme_text
    assert "[apps/backend/web/docs/review/](apps/backend/web/docs/review)" in readme_text
    assert "[doc/](doc)" in readme_text


def test_execution_docs_and_legacy_docs_remain_in_place():
    assert (BACKEND_WORKSPACE / "docs" / "task").is_dir()
    assert (BACKEND_WORKSPACE / "docs" / "review").is_dir()
    assert (REPO_ROOT / "doc" / "source" / "index.rst").is_file()
