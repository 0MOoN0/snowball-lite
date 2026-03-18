# -*- coding: utf-8 -*-
"""
通用可空字段模块

本模块定义了Flask-RESTX的通用可空字段类，解决Flask-RestX 1.3.0版本中
字段类型不支持allow_none=True参数的问题。

主要功能：
1. NullableField通用可空字段基类
2. 便捷的可空字段创建函数
3. 向后兼容的NullableDate类

作者: Assistant
创建时间: 2024
"""

from flask_restx import fields


class NullableField(fields.Raw):
    """通用的可空字段基类，支持null值验证"""
    
    def __init__(self, field_class, *args, **kwargs):
        """初始化可空字段
        
        Args:
            field_class: 要包装的字段类（如fields.String, fields.Integer等）
            *args, **kwargs: 传递给字段类的参数
        """
        super().__init__(*args, **kwargs)
        # 创建内部字段实例，但移除allow_none参数（Flask-RestX不支持）
        field_kwargs = {k: v for k, v in kwargs.items() if k != 'allow_none'}
        self._inner_field = field_class(*args, **field_kwargs)
        
        # 设置schema类型为联合类型（支持null）
        if hasattr(self._inner_field, '__schema_type__'):
            inner_type = self._inner_field.__schema_type__
            if isinstance(inner_type, list):
                self.__schema_type__ = inner_type + ['null'] if 'null' not in inner_type else inner_type
            else:
                self.__schema_type__ = [inner_type, 'null']
        else:
            self.__schema_type__ = ['null']
            
        # 继承内部字段的其他属性
        if hasattr(self._inner_field, '__schema_format__'):
            self.__schema_format__ = self._inner_field.__schema_format__
        if hasattr(self._inner_field, '__schema_example__'):
            self.__schema_example__ = self._inner_field.__schema_example__
    
    def format(self, value):
        """格式化值，支持None"""
        if value is None:
            return None
        return self._inner_field.format(value)
    
    def output(self, key, obj, ordered=False, **kwargs):
        """输出值，支持None"""
        if hasattr(obj, key) and getattr(obj, key) is None:
            return None
        return self._inner_field.output(key, obj, ordered, **kwargs)


# 便捷的可空字段创建函数
def nullable_string(*args, **kwargs):
    """创建可空字符串字段"""
    return NullableField(fields.String, *args, **kwargs)


def nullable_integer(*args, **kwargs):
    """创建可空整数字段"""
    return NullableField(fields.Integer, *args, **kwargs)


def nullable_float(*args, **kwargs):
    """创建可空浮点数字段"""
    return NullableField(fields.Float, *args, **kwargs)


def nullable_boolean(*args, **kwargs):
    """创建可空布尔字段"""
    return NullableField(fields.Boolean, *args, **kwargs)


def nullable_datetime(*args, **kwargs):
    """创建可空日期时间字段"""
    return NullableField(fields.DateTime, *args, **kwargs)


def nullable_date(*args, **kwargs):
    """创建可空日期字段"""
    return NullableField(fields.Date, *args, **kwargs)


# 保持向后兼容的NullableDate类
class NullableDate(fields.Date):
    """支持null值的Date字段（向后兼容）"""
    __schema_type__ = ['string', 'null']
    __schema_example__ = None
    
    def format(self, value):
        if value is None:
            return None
        return super().format(value)