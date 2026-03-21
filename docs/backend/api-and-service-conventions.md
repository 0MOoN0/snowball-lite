# API and Service Conventions

这份文档只保留当前还在用的接口和服务写法，目标是给后续新增代码一个统一落点。

## 当前原则

- 新增业务逻辑优先放 `apps/backend/web/services/`
- 新增接口优先沿用 Flask-RESTX `Namespace` + Marshmallow `Schema`
- 接口响应继续统一用 `R.ok(...)`、`R.fail(...)`、`R.paginate(...)`
- 日志继续用 `web.weblogger`
- lite 主线路径优先保证 SQLite 可跑、可测、可迁移，不再把 MySQL 专有写法当默认模板

## 服务层怎么写

服务层负责真正的业务处理，router 只负责接参数、调服务、返回结果。

推荐写法：

```python
result = SomeService().do_work(payload)
return R.ok(data=result)
```

不推荐把复杂判断、跨表逻辑、环境分支都堆进 router。

## 接口层怎么写

接口层现在默认按这套组合走：

1. 用 `Namespace` 组织一组相关接口。
2. 用 `Schema` 做输入校验和输出序列化。
3. 用 `R.ok(...)` 和 `R.fail(...)` 保持统一返回格式。
4. 需要文档展示时再用 `@api_ns.expect(...)`，不要把它当真正的校验逻辑。

## 返回值习惯

- 成功时优先返回 `R.ok(data=..., msg=...)`
- 明确失败时优先返回 `R.fail(msg=...)`
- 分页列表沿用 `R.paginate(...)`
- 能给出明确业务提示时，消息就直接写清楚

## 对旧写法的态度

- 旧的 Blueprint、Flask-RESTful、`reqparse` 代码还能维护，但不要继续给新功能扩这种写法
- 如果老接口要兼容，优先局部修，不要把新规范倒回旧风格
- 触及历史 MySQL 兼容路径时，别把 lite 主线的约定弄乱

## 和文档的关系

这份文档是稳定版入口，不替代执行文档。

- 任务设计继续留在 `apps/backend/web/docs/task/`
- 评审产物继续留在 `apps/backend/web/docs/review/`
- 阶段归档继续留在 `apps/backend/web/docs/desc/`

## 相关文档

- [Backend Docs README](README.md)
- [Backend System Overview](system-overview.md)
- [Runtime Config](runtime-config.md)
