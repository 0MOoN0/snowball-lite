from web.routers.MenuRouters import menu_bp
from web.common.api_factory import get_api

# GridTypeAnalysisResultRouters已改造为Flask-RestX架构，不再使用blueprint
from web.routers.asset.AssetCodeRouters import asset_code_bp

# AssetListRouters已改造为Flask-RestX架构，不再使用blueprint
from web.routers.asset.AssetRelationRouters import asset_relations_bp
from web.routers.asset.AssetRouters import asset_bp
from web.routers.category.CategoryListRouters import category_list_bp
from web.routers.category.CategoryRouter import category_bp
from web.routers.charts import charts_bp
from web.routers.grid.GridDetailRouters import grid_detail_bp
from web.routers.grid.GridTypeDetailRouters import (
    grid_type_detail_list_bp,
    grid_type_detail_current_bp,
    grid_type_detail_file_bp,
    grid_type_detail_file_sync_bp,
)
from web.routers.grid.GridTypeRouters import grid_type_bp

# from web.routers.notice.NotificationRoueters import (
#     notification_list_bp,
#     notification_count_bp,
#     notification_bp,
# )
from web.routers.record.GridRecordAllSyncRouters import grid_record_all_sync_bp
from web.routers.record.IRecordRouters import irecord_bp
from web.routers.system.system_data_routers import system_bp
from web.routers.system.token_test_routers import token_test_bp
from web.routers.user.UserRouters import user_bp


def init_app(app):
    app.logger.debug("### 加载routers模块")
    from web.routers.grid.grid_routers import grid_bp, grid_list_bp

    app.register_blueprint(grid_bp)
    app.register_blueprint(grid_detail_bp)
    app.register_blueprint(grid_list_bp)
    app.register_blueprint(menu_bp)
    from web.routers.record.record_routers import record_file_bp

    app.register_blueprint(irecord_bp)

    app.register_blueprint(record_file_bp)
    app.register_blueprint(grid_record_all_sync_bp)
    app.register_blueprint(asset_bp)
    app.register_blueprint(category_list_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(asset_code_bp)
    # asset_list_bp已改造为Flask-RestX架构，通过命名空间自动注册
    # grid_type
    # grid_type_analysis_result_bp已改造为Flask-RestX架构，通过命名空间自动注册
    app.register_blueprint(grid_type_bp)
    app.register_blueprint(grid_type_detail_list_bp)
    app.register_blueprint(grid_type_detail_current_bp)
    app.register_blueprint(grid_type_detail_file_bp)
    app.register_blueprint(grid_type_detail_file_sync_bp)
    # scheduler
    # app.register_blueprint(scheduler_bp)
    # notification
    # app.register_blueprint(notification_bp)
    # app.register_blueprint(notification_list_bp)
    # app.register_blueprint(notification_count_bp)
    # charts
    app.register_blueprint(charts_bp)
    # user-api
    app.register_blueprint(user_bp)
    app.register_blueprint(asset_relations_bp)
    # scheduler
    if app.config.get("SCHEDULER_AVAILABLE", False):
        from web.routers.scheduler.scheduler_job_list_routers import (
            scheduler_job_list_bp,
        )
        from web.routers.scheduler.scheduler_job_log_routers import (
            scheduler_job_log_bp,
        )
        from web.routers.scheduler.scheduler_job_operation_routers import (
            scheduler_job_operation_bp,
        )
        from web.routers.scheduler.scheduler_persistence_policy_routers import (
            scheduler_persistence_policy_bp,
        )
        from web.routers.scheduler.scheduler_routers import scheduler_bp

        app.register_blueprint(scheduler_bp)
        app.register_blueprint(scheduler_job_operation_bp)
        app.register_blueprint(scheduler_job_list_bp)
        app.register_blueprint(scheduler_job_log_bp)
        app.register_blueprint(scheduler_persistence_policy_bp)
    else:
        app.logger.info("由于调度器未启用或初始化失败，跳过 scheduler 路由注册")
    # system
    app.register_blueprint(system_bp)
    # app.register_blueprint(system_settings_bp)
    from web.routers.system import system_settings_routers
    from web.routers.system import enum_version_routers  # 确保枚举版本路由被注册
    from web.routers.system import enum_dynamic_routers  # 确保动态枚举路由被注册
    from web.routers.notice import notification_detail_routers
    from web.routers.notice import notification_list_routers
    from web.routers.notice import notification_count_routers
    from web.routers.analysis import grid_analysis_result_routers
    from web.routers.analysis import (
        grid_type_analysis_result_routers,
    )  # 确保Flask-RestX命名空间被注册
    from web.routers.asset import asset_list_routers  # 确保AssetListRouters路由被注册
    from web.routers.asset import asset_routers  # 确保AssetRouters路由被注册
    from web.routers.index import index_list_routers  # 确保IndexListRouters路由被注册
    from web.routers.index import (
        index_detail_routers,
    )  # 确保IndexDetailRouters路由被注册
    from web.routers.asset import asset_alias_detail_routers  # 确保单个别名路由被注册
    from web.routers.asset import asset_alias_list_routers  # 确保别名列表批量路由被注册
    from web.routers.index import index_alias_detail_routers  # 确保指数别名路由被注册
    from web.routers.index import index_alias_list_routers  # 确保指数别名批量路由被注册
    from web.routers.charts import transaction_charts_routers  # 确保交易图表路由被注册
    from web.routers.charts import dashboard_routers  # 确保仪表板路由被注册
    from web.routers.record import record_list_routers  # 确保交易记录列表路由被注册
    from web.routers.record import record_file_routers  # 确保交易记录文件路由被注册

    # token_test
    app.register_blueprint(token_test_bp)
    app.logger.debug("routers模块加载完成 ###")
