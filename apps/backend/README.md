# 后端工作区

这里是后端工作区的入口目录。真实后端代码位于当前目录下的 `web/`，常用运行命令也都从这里启动。`sitecustomize.py` 会在从这个目录启动 Python 时自动把 `apps/backend` 加进 `sys.path`。

常用启动方式：

```bash
cd apps/backend
python -m web.lite_application
SNOW_APP_STATUS=dev python -m web.application
gunicorn -c web/gunicorn.config.py web.application:app
```

Lite 模式会继续使用 `apps/backend/web/docs` 里的评审和任务工件，不会把这条路径切断。
