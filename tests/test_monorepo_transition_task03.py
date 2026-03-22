from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = REPO_ROOT / "apps" / "frontend"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_frontend_runtime_profiles_distinguish_lite_and_dev():
    lite_env = _read_text(FRONTEND_ROOT / ".env.lite")
    dev_env = _read_text(FRONTEND_ROOT / ".env.dev")
    package = json.loads(_read_text(FRONTEND_ROOT / "package.json"))

    assert "VITE_RUNTIME_PROFILE=lite" in lite_env
    assert "VITE_PROXY_TARGET=http://127.0.0.1:5001" in lite_env
    assert "VITE_ENABLE_SCHEDULER=true" in lite_env
    assert "VITE_ENABLE_SYSTEM_TOKEN=false" in lite_env

    assert "VITE_RUNTIME_PROFILE=dev" in dev_env
    assert "VITE_PROXY_TARGET=http://127.0.0.1:15000" in dev_env
    assert "VITE_ENABLE_SCHEDULER=true" in dev_env
    assert "VITE_ENABLE_SYSTEM_TOKEN=true" in dev_env

    assert package["scripts"]["dev"] == "vite --mode lite"
    assert package["scripts"]["dev:lite"] == "vite --mode lite"
    assert package["scripts"]["dev:dev"] == "vite --mode dev"
    assert package["scripts"]["build:lite"] == "pnpm run ts:check && vite build --mode lite"


def test_frontend_runtime_alignment_files_encode_backend_boundaries():
    vite_config = _read_text(FRONTEND_ROOT / "vite.config.ts")
    runtime_profile = _read_text(FRONTEND_ROOT / "src/config/runtimeProfile.ts")
    runtime_session = _read_text(FRONTEND_ROOT / "src/config/runtimeSession.ts")
    main_entry = _read_text(FRONTEND_ROOT / "src/main.ts")
    scheduler_view = _read_text(FRONTEND_ROOT / "src/views/Snow/Setting/Scheduler/Scheduler.vue")
    data_setting_view = _read_text(FRONTEND_ROOT / "src/views/Snow/Setting/Data/DataSetting.vue")
    frontend_readme = _read_text(FRONTEND_ROOT / "README.md")
    root_readme = _read_text(REPO_ROOT / "README.md")

    assert "const proxyTarget = env.VITE_PROXY_TARGET || 'http://127.0.0.1:5001'" in vite_config
    assert "runtimeCapabilityFlags" in runtime_profile
    assert "if (runtimeProfile !== 'lite')" in runtime_session
    assert "wsCache.set(appModules.userInfo, liteRuntimeUser)" in runtime_session
    assert "wsCache.set('dynamicRouter', false)" in runtime_session
    assert "bootstrapRuntimeSession()" in main_entry
    assert "当前运行配置未开启 scheduler" in scheduler_view
    assert "lite 口径下不支持系统 token / Redis 相关配置页" in data_setting_view
    assert "pnpm run dev:dev" in frontend_readme
    assert "python -m web.lite_application" in frontend_readme
    assert "lite 前端会直接注入本地会话" in frontend_readme
    assert "scheduler 本身默认开启" in root_readme
