from enum import Enum


class TorxiongAdapterEnum(str, Enum):
    # GP(股票),ZS(指数),GP类型可以细分为GP-A即A股,GP-B为B股,GP-A-KCB为科创板A股.
    STOCK = 'GP'
    """
    股票
    """
    INDEX = 'ZS'
    """
    指数
    """
    STOCK_A = 'GP-A'
    """
    A股
    """
    STOCK_B = 'GP-B'
    """
    B股
    """
    STOCK_A_KCB = 'GP-A-KCB'
    """
    科创板A股
    """
    STOCK_A_YCB = 'GP-A-CYB'
    """
    A股创业板
    """
    STOCK_A_ZXB = 'GP-A-ZXB'
    """
    A股中小板
    """