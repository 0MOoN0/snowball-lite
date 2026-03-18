from web.databox.base import databox


def init_app(app):
    # databox模块依赖cache模块，初始化databox之前需要先初始化cache模块
    app.logger.debug('### 加载databox模块')
    databox.init_app(app)
    app.logger.debug('databox模块加载完毕 ###')