"""
通用服务模块

该模块提供了通用的继承更新服务框架，包括：
- BaseInheritanceUpdateService: 核心抽象基类
- MultiDatabaseTransactionManager: 多数据库事务管理
- ModelRegistry: 模型注册表
- DynamicSchemaHandler: 动态Schema处理
- ModelConversionRules: 模型转换规则配置

作者: AI Assistant
创建时间: 2024年1月
版本: 1.0.0
"""

from .base_inheritance_update_service import BaseInheritanceUpdateService

__all__ = [
    # 核心服务类
    'BaseInheritanceUpdateService',
]