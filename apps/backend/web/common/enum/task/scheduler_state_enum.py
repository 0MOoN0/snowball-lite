from enum import Enum, IntEnum


class SchedulerStateEnum(IntEnum):
    """
    SchedulerStateEnum
    """

    SUBMITTED = 0
    """
    已提交
    """
    EXECUTED = 1
    """
    已执行
    """
    ERROR = 2
    """
    执行异常
    """
    MISSED = 3
    """
    错过执行
    """