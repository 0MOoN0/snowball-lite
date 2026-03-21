from abc import abstractmethod, ABC

from web.common.enum import TaskEnum
from web.decorator import singleton
from web.task.TaskModel import TaskItem


class TaskStrategy(ABC):
    @abstractmethod
    def do_execute(self, task_item: TaskItem) -> bool:
        pass


@singleton
class InitFundDataStrategy(TaskStrategy):
    """
    初始化基金数据的任务策略
    """

    def do_execute(self, task_item: TaskItem) -> bool:
        # 获取资产代码
        # asset_code: AssetCode = db.session.query(AssetCode) \
        #     .join(TaskAsset, AssetCode.asset_id == TaskAsset.asset_id, isouter=True) \
        #     .filter(TaskAsset.task_id == task_item.task.id) \
        #     .first()
        # try:
        #     # 初始化资产
        #     asset_service.init_fund_asset_data(asset_code.asset_id, code_ttjj=asset_code.code_ttjj,
        #                                        code_xq=asset_code.code_xq)
        # except Exception as e:
        #     logger.error('资产ID： %s ，初始化基金数据失败，异常信息：%s' % (asset_code.asset_id, e))
        #     return False
        return True


@singleton
class InitIndexDataStrategy(TaskStrategy):
    """
    初始化指数数据的任务策略

    """

    def do_execute(self, task_item: TaskItem) -> bool:
        # 获取资产代码
        # asset_code: AssetCode = db.session.query(AssetCode) \
        #     .join(TaskAsset, AssetCode.asset_id == TaskAsset.asset_id, isouter=True) \
        #     .filter(TaskAsset.task_id == task_item.task.id) \
        #     .first()
        # try:
        #     # 初始化资产
        #     asset_service.init_index_asset_data(asset_id=asset_code.asset_id, code_index=asset_code.code_index)
        # except Exception as e:
        #     logger.error('资产ID： %s ，初始化指数数据失败，异常信息：%s' % (asset_code.asset_id, e))
        #     return False
        return True


@singleton
class TaskContext:

    def __init__(self):
        self.strategies = dict()
        self.strategies.update({TaskEnum.TaskBusinessTypeEnum.INIT_FUND_ASSET.value: InitFundDataStrategy(),
                                TaskEnum.TaskBusinessTypeEnum.INIT_INDEX_ASSET.value: InitIndexDataStrategy()})

    def execute(self, task_item: TaskItem) -> bool:
        """
        根据业务类型选择策略执行任务
        Args:
            task_item (TaskItem):   任务对象

        Returns:
            执行结果，True或False
        """
        strategy: TaskStrategy = self.strategies.get(task_item.task.business_type)
        return strategy.do_execute(task_item)


task_context = TaskContext()
