"""
模型注册模块
专门用于导入所有模型类，确保它们被注册到SQLAlchemy元数据中
"""

# 资产相关模型
from web.models.asset.asset import Asset
from web.models.asset.asset_code import AssetCode
from web.models.asset.asset_category import AssetCategory
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.models.asset.AssetFundFeeRule import AssetFundFeeRule
from web.models.asset.AssetHoldingData import AssetHoldingData
from web.models.asset.asset_fund import AssetFund, AssetFundETF, AssetFundLOF
from web.models.asset.asset_alias import AssetAlias

# 分类相关模型
from web.models.category.Category import Category

# 任务相关模型
from web.models.task.Task import Task
from web.models.task.TaskAsset import TaskAsset
from web.models.task.TaskLog import TaskLog

# 网格相关模型
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridDetail import GridDetail
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.models.grid.GridTypeRecord import GridTypeRecord

# 分析相关模型
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.analysis.amount_trade_analysis_data import AmountTradeAnalysisData
from web.models.analysis.GridGridAnalysisData import GridGridAnalysisData
from web.models.analysis.GridTypeGridAnalysisData import GridTypeGridAnalysisData

# 指数相关模型
from web.models.index.index_base import IndexBase
from web.models.index.index_stock import StockIndex
from web.models.index.index_alias import IndexAlias

# 其他模型
from web.models.Menu import Menu
from web.models.IRecord import IRecord
from web.models.GridRecord import GridRecord
from web.models.notice.Notification import Notification
from web.models.notice.notification_log import NotificationLog
from web.models.record.record import Record
from web.models.record.trade_reference import TradeReference
from web.models.scheduler.scheduler_log import SchedulerLog
from web.models.scheduler.scheduler_job_state import SchedulerJobState
from web.models.stock_fund import StockFund

# 导出所有模型类的列表，便于其他模块使用
# 在文件顶部的导入部分添加
from web.models.setting.system_settings import Setting

# 在 __all__ 列表中添加
__all__ = [
    # 资产相关
    "Asset",
    "AssetCode",
    "AssetCategory",
    "AssetFundDailyData",
    "AssetFundFeeRule",
    "AssetHoldingData",
    "AssetFund",
    "AssetFundETF",
    "AssetFundLOF",
    "AssetAlias",
    # 分类相关
    "Category",
    # 任务相关
    "Task",
    "TaskAsset",
    "TaskLog",
    # 网格相关
    "Grid",
    "GridType",
    "GridDetail",
    "GridTypeDetail",
    "GridTypeRecord",
    # 分析相关
    "TradeAnalysisData",
    "GridTradeAnalysisData",
    "AmountTradeAnalysisData",
    "GridGridAnalysisData",
    "GridTypeGridAnalysisData",
    # 指数相关
    "IndexBase",
    "StockIndex",
    "IndexAlias",
    # 其他
    "Menu",
    "IRecord",
    "GridRecord",
    "Notification",
    "NotificationLog",
    "Record",
    "TradeReference",
    "SchedulerLog",
    "SchedulerJobState",
    "StockFund",
    # 设置相关
    "Setting",
]
