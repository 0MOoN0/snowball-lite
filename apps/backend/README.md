# 后端工作区

这里是后端工作区的入口目录。真实后端代码位于当前目录下的 `web/`，仓库根的 `web` 只是一个兼容符号链接。`sitecustomize.py` 会在从这个目录启动 Python 时自动把仓库根加回 `sys.path`，这样 `xalpha/` 仍然可以直接导入。

常用启动方式：

```bash
cd apps/backend
python -m web.lite_application
SNOW_APP_STATUS=dev python -m web.application
gunicorn -c web/gunicorn.config.py web.application:app
```

Lite 模式会继续使用仓库级 `web/docs` 里的评审和任务工件，不会把这条路径切断。
