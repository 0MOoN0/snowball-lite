# -*- coding: utf-8 -*-
"""
@File    ：notification_config_service.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/14 
@Description: 通知配置服务，负责从数据库获取通知相关配置
"""

import json
from typing import Optional, List
from web.decorator import singleton
from web.models.setting.system_settings import Setting
from web.weblogger import debug, error


@singleton
class NotificationConfigService:
    """通知配置服务"""
    
    def __init__(self):
        # 配置缓存，避免频繁查询数据库
        self._config_cache = {}
    
    def get_setting_by_key(self, key: str, default_value: str = None) -> Optional[str]:
        """
        根据键获取配置项值
        
        Args:
            key (str): 配置项键
            default_value (str): 默认值
            
        Returns:
            Optional[str]: 配置项值，如果不存在则返回默认值
        """
        try:
            # 先从缓存中获取
            if key in self._config_cache:
                return self._config_cache[key]
                
            # 从数据库查询
            setting = Setting.query.filter_by(key=key).first()
            if setting:
                # 对于 JSON 类型，直接返回原始字符串值，不进行类型转换
                if setting.setting_type == 'json':
                    value = setting.value
                else:
                    value = str(setting.get_typed_value())
                # 缓存结果
                self._config_cache[key] = value
                return value
            else:
                debug(f"配置项 {key} 不存在，使用默认值: {default_value}")
                return default_value
        except Exception as e:
            error(f"获取配置项 {key} 失败: {str(e)}")
            return default_value
    
    def get_channels_for_business(self, business_type: str) -> List[str]:
        """
        根据业务类型获取通知渠道列表
        
        Args:
            business_type (str): 业务类型 (grid_trade, system_runing, message_remind, daily_report)
            
        Returns:
            List[str]: 通知渠道名称列表
        """
        # 构造业务类型配置键，格式为：notification_business_type.{business_type}
        config_key = f"notification_business_type.{business_type}"
        
        # 获取业务类型特定的渠道配置（JSON数组格式）
        channels_json = self.get_setting_by_key(config_key)
        
        if channels_json:
            try:
                channels = json.loads(channels_json)
                if channels and len(channels) > 0:
                    # 返回所有配置的渠道
                    return channels
            except (json.JSONDecodeError, IndexError) as e:
                error(f"解析业务类型 {business_type} 的渠道配置失败: {str(e)}")
        
        # 如果没有配置或解析失败，则使用默认渠道
        return [self.get_default_channel()]
    
    def get_channel_for_business(self, business_type: str) -> str:
        """
        根据业务类型获取第一个通知渠道（保持向后兼容）
        
        Args:
            business_type (str): 业务类型 (grid_trade, system_runing, message_remind, daily_report)
            
        Returns:
            str: 通知渠道名称
        """
        channels = self.get_channels_for_business(business_type)
        return channels[0] if channels else self.get_default_channel()
    
    def get_default_channel(self) -> str:
        """
        获取默认通知渠道
        
        Returns:
            str: 默认通知渠道名称
        """
        return self.get_setting_by_key("notification.default.channel", "notification_sender.wecom")
    
    def is_channel_enabled(self, channel: str) -> bool:
        """
        检查渠道是否启用
        
        Args:
            channel (str): 渠道名称（格式：notification_sender.xxx）
            
        Returns:
            bool: 渠道是否启用
        """
        # 检查渠道配置是否存在且有值
        channel_config = self.get_setting_by_key(channel)
        # 如果配置存在且不为空，则认为渠道已启用
        return channel_config is not None and channel_config.strip() != ""
    
    def clear_cache(self):
        """
        清空配置缓存
        """
        self._config_cache.clear()
        debug("通知配置缓存已清空")
    
    def refresh_config(self, key: str = None):
        """
        刷新配置缓存
        
        Args:
            key (str): 指定刷新的配置键，如果为None则清空所有缓存
        """
        if key:
            if key in self._config_cache:
                del self._config_cache[key]
                debug(f"配置项 {key} 缓存已刷新")
        else:
            self.clear_cache()


# 创建单例实例
notification_config_service: NotificationConfigService = NotificationConfigService()