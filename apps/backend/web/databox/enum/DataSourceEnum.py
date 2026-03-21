from enum import Enum


class DataSourceEnum(Enum):
    """
    数据源枚举
    定义系统支持的各种数据源
    """
    AKSHARE = "AkShare"
    AKSHARE_CSINDEX = "AkShare-CSINDEX"
    TUSHARE = "TuShare"
    WIND = "Wind"
    EASTMONEY = "EastMoney"
    SINA = "Sina"
    YAHOO = "Yahoo"
    CUSTOM = "Custom"