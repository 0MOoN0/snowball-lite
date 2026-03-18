from numpy import number

from web.models.asset.asset_code import AssetCode


class TaskAssetStrategyContext:
    """
    资产任务策略上下文
    """

    def __init__(self, strategy):
        """
        方法内容: 初始化资产任务策略上下文
        设计目的: 通过资产任务策略初始化资产任务策略上下文
        Args:
        """
        self.do_strategy = strategy

    def init_asset(self, asset_code: AssetCode, **kwargs):
        """
        方法内容：根据初始化策略执行策略内容
        设计目的：
        Args:
            asset_code(AssetCode)：资产代码
            **kwargs: 其他参数

        Returns:

        """
        self.do_strategy(asset_code, kwargs)


task_asset_strategy_context = TaskAssetStrategyContext()
