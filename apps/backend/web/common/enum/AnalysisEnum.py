from enum import IntEnum


class TransactionAnalysisTypeEnum(IntEnum):
    """
    交易分析数据所属类型
    0-网格，1-网格类型，2-网格策略
    """
    GRID = 0
    """
    0 - 网格
    """
    GRID_TYPE = 1
    """
    1 - 网格类型
    """
    GRID_STRATEGY = 2
    """
    2 - 网格策略
    """
    AMOUNT = 3
    """
    3 - 整体持有仓位
    """


class GridTransactionAnalysisBusinessTypeEnum(IntEnum):
    """
    网格交易分析业务类型枚举
    0-网格类型交易分析，1-网格交易分析，2-网格策略交易分析
    """
    GRID_TYPE_ANALYSIS = 0
    """
    0 - 网格类型交易分析
    """
    GRID_ANALYSIS = 1
    """
    1 - 网格交易分析
    """
    GRID_STRATEGY_ANALYSIS = 2
    """
    2 - 网格策略交易分析
    """
