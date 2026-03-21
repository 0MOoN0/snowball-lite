# Round 01 Review

## 范围

- `/Users/leon/projects/snowball-lite/apps/backend/web/settings.py`
- `/Users/leon/projects/snowball-lite/apps/backend/web/__init__.py`
- `/Users/leon/projects/snowball-lite/apps/backend/web/routers/__init__.py`
- `/Users/leon/projects/snowball-lite/apps/backend/web/scheduler/__init__.py`
- `/Users/leon/projects/snowball-lite/apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py`
- `/Users/leon/projects/snowball-lite/README.md`

## Findings

1. 中风险：scheduler 测试清理依赖监听器结构时，初版清理方式会因为 `_listeners` 不是预期类型而留下测试串扰风险。
   - 位置：
     - `/Users/leon/projects/snowball-lite/apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py`
   - 说明：
     - 初版清理假设监听器容器结构固定。
     - 实际运行下 `_listeners` 是可直接清空的列表结构，需要按实际对象清理，否则多条测试之间可能累积状态。

## 处理结论

- 已在下一轮修复里调整监听器清理方式，并补充回归测试保证不会再次串状态。
