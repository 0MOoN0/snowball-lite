from datetime import datetime
from typing import Union

from web.scheduler.base import scheduler
from web.services.analysis.transaction_analysis_service import AmountTransactionAnalysisService, TradeAnalysisService, \
    trade_analysis_all_the_time


# 删除中间包装函数，改为在具体任务函数中直接构造并发送通知


# 每天晚上九点分析所有交易数据
@scheduler.task(id='analysis_scheduler.to_analysis_all_transaction', name='每日交易数据分析（21:00）', trigger='cron', hour=21,
                minute=0)
def to_analysis_all_transaction(start: Union[datetime, str] = None, end: Union[datetime, str] = None):
    """
    使用定时任务分析所有交易。

    Args:
        start (Union[datetime, str], optional): 分析的起始时间，默认为None，表示使用当前日期。
            可以为datetime对象或日期格式的字符串，如果为字符串则尝试转换为datetime对象。
            Defaults to None.
        end (Union[datetime, str], optional): 分析的结束时间，默认为None，表示使用当前日期。
            可以为datetime对象或日期格式的字符串，如果为字符串则尝试转换为datetime对象。
            Defaults to None.

    Returns:
        None

    """
    with scheduler.app.app_context():
        trade_service: TradeAnalysisService = AmountTransactionAnalysisService()
        trade_service.trade_analysis(start=start, end=end)


@scheduler.task(id='analysis_scheduler.analysis_all_the_time', name='历史全量交易数据分析（一次性任务）', trigger='date',
                run_date='2099-08-31')
def analysis_all_the_time(start: Union[datetime, str] = None, end: Union[datetime, str] = None):
    """
    定时任务：分析所有时间的所有种类交易。

    Args:
        start (Union[datetime, str], optional): 分析的开始时间，默认为None。
                如果为datetime类型，则直接使用该时间；如果为str类型，则尝试将其转换为datetime类型。
        end (Union[datetime, str], optional): 分析的结束时间，默认为None。
                如果为datetime类型，则直接使用该时间；如果为str类型，则尝试将其转换为datetime类型。

    Returns:
        None

    """
    with scheduler.app.app_context():
        trade_analysis_all_the_time(start=start, end=end)
