# Round 01 Review

## 范围

- `/Users/leon/projects/snowball-lite/apps/backend/web/common/utils/backend_paths.py`
- `/Users/leon/projects/snowball-lite/apps/backend/web/settings.py`
- `/Users/leon/projects/snowball-lite/apps/backend/web/__init__.py`
- `/Users/leon/projects/snowball-lite/apps/backend/web/webtest/lite_runtime_guard.py`
- `/Users/leon/projects/snowball-lite/apps/backend/web/webtest/lite_runtime_fixtures.py`
- `/Users/leon/projects/snowball-lite/apps/backend/web/webtest/conftest.py`
- `/Users/leon/projects/snowball-lite/apps/backend/web/webtest/lite/test_backend_workspace_paths.py`
- `/Users/leon/projects/snowball-lite/apps/backend/web/webtest/lite/test_lite_database_layering.py`
- `/Users/leon/projects/snowball-lite/README.md`
- `/Users/leon/projects/snowball-lite/apps/backend/web/docs/环境变量配置指南.md`

## Findings

1. 高风险：pytest 下的 lite 数据库隔离还停在 fixture 层，不是运行入口层的硬保护。
   - 位置：
     - `/Users/leon/projects/snowball-lite/apps/backend/web/webtest/lite_runtime_guard.py`
     - `/Users/leon/projects/snowball-lite/apps/backend/web/webtest/lite_runtime_fixtures.py`
     - `/Users/leon/projects/snowball-lite/apps/backend/web/webtest/conftest.py`
     - `/Users/leon/projects/snowball-lite/apps/backend/web/settings.py`
     - `/Users/leon/projects/snowball-lite/apps/backend/web/__init__.py`
   - 说明：
     - 当前 guard 只在 fixture 自己生成测试 SQLite 路径时调用。
     - 任意测试如果手动 `monkeypatch.setenv("LITE_DB_PATH", ...)` 后直接 `create_app("lite")`，仍然可以绕过保护。
     - 这会让 README 和环境变量文档里“默认测试不能指向 stable/prod 或 dev 长期库”的说法强于实际代码契约。

## 处理结论

- 已在下一轮修复里把 guard 下沉到公共 helper，并接入 `create_app("lite")` 的 pytest 运行链路。
