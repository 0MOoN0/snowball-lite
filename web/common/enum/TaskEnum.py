from enum import Enum


class TaskStatusEnum(Enum):
    """
    任务状态枚举
    0未执行，任务处于需要执行但未添加入队列的状态
    1等待执行，任务已经加入执行队列中
    2执行中
    3执行完毕
    """
    NOT_EXECUTED = 0
    WAITING = 1
    EXECUTING = 2
    EXECUTED = 3


class TaskTypeEnum(Enum):
    """
    0-一次性任务
    1-定时任务
    """
    DISPOSABLE = 0
    SCHEDULED = 1


class TaskBusinessTypeEnum(Enum):
    """
    任务业务类型枚举
    0-初始化基金数据
    1-更新收益数据
    2-同步资产数据
    3-初始化指数数据
    """
    INIT_FUND_ASSET = 0
    UPDATE_REVENUE = 1
    SYNC_ASSET = 2
    INIT_INDEX_ASSET = 3
