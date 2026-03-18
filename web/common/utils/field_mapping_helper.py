"""
字段名称转换工具

该模块提供了字段名称转换的工具函数，支持：
- 驼峰命名与下划线命名的转换

"""

import re
from typing import Dict, Any


class FieldMappingHelper:
    """字段名称转换工具类"""
    
    @staticmethod
    def camel_to_snake(name: str) -> str:
        """
        将驼峰命名转换为下划线命名
        
        Args:
            name: 驼峰命名的字符串
            
        Returns:
            str: 下划线命名的字符串
        """
        # 在大写字母前插入下划线，然后转换为小写
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def camel_to_snake_case(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        批量将字典中的驼峰命名字段转换为下划线命名
        
        Args:
            data: 原始数据字典
            
        Returns:
            Dict[str, Any]: 转换后的数据字典
        """
        if not isinstance(data, dict):
            return data
        
        converted_data = {}
        
        for key, value in data.items():
            new_key = FieldMappingHelper.camel_to_snake(key)
            
            # 递归处理嵌套字典
            if isinstance(value, dict):
                converted_data[new_key] = FieldMappingHelper.camel_to_snake_case(value)
            elif isinstance(value, list):
                converted_data[new_key] = [
                    FieldMappingHelper.camel_to_snake_case(item) 
                    if isinstance(item, dict) else item 
                    for item in value
                ]
            else:
                converted_data[new_key] = value
        
        return converted_data