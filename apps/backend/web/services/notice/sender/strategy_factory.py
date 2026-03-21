# -*- coding: utf-8 -*-
"""
发送策略工厂
用于根据渠道名称创建对应的发送策略实例
"""

from typing import Dict, Type, Optional
from web.decorator import singleton
from web.services.notice.sender.sender_strategy import (
    SenderStrategy, SenderContext, ServerChenSenderStrategy, 
    TelegramBotSenderStrategy, PushPlusSenderStrategy, WeComSenderStrategy
)
from web.common.enum.webEnum import NotificationChannelEnum
from web.weblogger import debug, error


@singleton
class SenderStrategyFactory:
    """
    发送策略工厂类
    """
    
    def __init__(self):
        self._strategies: Dict[str, Type[SenderStrategy]] = {}
        self._strategy_cache: Dict[str, SenderStrategy] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """
        注册默认的发送策略
        """
        self.register_strategy("serverchan", ServerChenSenderStrategy)
        self.register_strategy("telegram", TelegramBotSenderStrategy)
        self.register_strategy("pushplus", PushPlusSenderStrategy)
        self.register_strategy("wecom", WeComSenderStrategy)
        
        debug(f"已注册发送策略: {list(self._strategies.keys())}")
    
    def register_strategy(self, channel: str, strategy_class: Type[SenderStrategy]):
        """
        注册发送策略
        
        Args:
            channel (str): 渠道名称
            strategy_class (Type[SenderStrategy]): 策略类
        """
        self._strategies[channel] = strategy_class
        debug(f"注册发送策略: {channel} -> {strategy_class.__name__}")
    
    def get_strategy(self, channel: str) -> Optional[SenderStrategy]:
        """
        根据渠道名称获取发送策略
        
        Args:
            channel (str): 渠道名称（格式：notification_sender.xxx）
            
        Returns:
            Optional[SenderStrategy]: 策略实例，如果不存在则返回None
        """
        # 将数据库中的渠道名称格式转换为策略名称
        strategy_name = self._convert_channel_to_strategy_name(channel)
        
        if strategy_name not in self._strategies:
            error(f"未找到渠道 {channel} 对应的发送策略 (策略名称: {strategy_name})")
            return None
        
        # 使用缓存避免重复创建实例
        if strategy_name not in self._strategy_cache:
            strategy_class = self._strategies[strategy_name]
            try:
                self._strategy_cache[strategy_name] = strategy_class()
                debug(f"创建发送策略实例: {strategy_name}")
            except Exception as e:
                error(f"创建发送策略实例失败: {strategy_name}, 错误: {str(e)}")
                return None
        
        return self._strategy_cache[strategy_name]
    
    def create_context(self, channel: str) -> Optional[SenderContext]:
        """
        创建发送上下文
        
        Args:
            channel (str): 渠道名称（格式：notification_sender.xxx）
            
        Returns:
            Optional[SenderContext]: 发送上下文，如果创建失败则返回None
        """
        strategy = self.get_strategy(channel)
        if strategy is None:
            return None
        
        return SenderContext(strategy)
    
    def clear_cache(self):
        """
        清空策略缓存
        """
        self._strategy_cache.clear()
        debug("已清空发送策略缓存")
    
    def _convert_channel_to_strategy_name(self, channel: str) -> str:
        """
        将数据库中的渠道名称格式转换为策略名称
        
        Args:
            channel (str): 数据库中的渠道名称（格式：notification_sender.xxx）
            
        Returns:
            str: 策略名称
        """
        # 移除前缀 "notification_sender."
        if channel.startswith("notification_sender."):
            strategy_name = channel.replace("notification_sender.", "")
            # 处理特殊映射
            if strategy_name == "server_chan":
                return "serverchan"
            elif strategy_name == "telegram_bot":
                return "telegram"
            else:
                return strategy_name
        else:
            # 如果不是标准格式，直接返回原名称
            return channel
    
    def get_supported_channels(self) -> list:
        """
        获取支持的渠道列表
        
        Returns:
            list: 支持的渠道名称列表（数据库格式：notification_sender.xxx）
        """
        # 将策略名称转换为数据库中的渠道名称格式
        channels = []
        for strategy_name in self._strategies.keys():
            if strategy_name == "serverchan":
                channels.append("notification_sender.server_chan")
            elif strategy_name == "telegram":
                channels.append("notification_sender.telegram_bot")
            elif strategy_name == "pushplus":
                channels.append("notification_sender.pushplus")
            elif strategy_name == "wecom":
                channels.append("notification_sender.wecom")
        return channels


# 创建单例实例
sender_strategy_factory: SenderStrategyFactory = SenderStrategyFactory()