from enum import Enum, auto


class DataBoxAdapterEnum(Enum):
    """
    DataBox的数据适配器来源枚举
    """
    XA = 'xa'
    TORXIONG = 'torxiong'
    AKSHARE = 'akshare'
    XA_SERVICE = 'xa_service'


class CodeTypeEnum(Enum):
    """
    代码类型枚举
    """
    INDEX = 'INDEX'
    TTJJ = 'TTJJ'
    XQ = 'XQ'


class DataBoxEnums:
    def __init__(self):
        self.dataBoxAdapterEnum = DataBoxAdapterEnum
        self.codeTypeEnum = CodeTypeEnum
