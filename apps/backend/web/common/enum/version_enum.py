from enum import Enum


class VersionKeyEnum(Enum):
    """
    Redis版本键枚举
    用于统一管理Redis中的版本键名称
    """
    ENUM = "version:enum"
    """
    枚举版本键
    """
    CONFIG = "version:config"
    """
    配置版本键
    """
    SCHEMA = "version:schema"
    """
    数据库架构版本键
    """