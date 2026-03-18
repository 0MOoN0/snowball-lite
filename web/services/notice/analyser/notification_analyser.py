# -*- coding: UTF-8 -*-
"""
@File    ：notification_analyser.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/9/16 23:25
"""
import copy
import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Union

from web.models.grid.GridTypeDetail import GridTypeDetail, GridTypeDetailVOSchema
from web.models.notice.Notification import Notification
from web.weblogger import debug, error


class BusinessType(Enum):
    """
    业务类型枚举
    """
    GRID_TRADE = 0      # 网格交易通知
    MESSAGE_REMIND = 1  # 消息提醒通知
    SYSTEM_RUNNING = 2  # 系统运行通知
    DAILY_REPORT = 3    # 日报通知
    CB_SUBSCRIBE = 4    # 可转债申购通知


class ChannelType(Enum):
    """
    发送渠道类型枚举
    """
    BOT = "bot"           # 机器人渠道 (Telegram, 企业微信等)
    HTML = "html"         # HTML渠道 (邮件, PushPlus等)
    MARKDOWN = "markdown" # Markdown渠道 (Server酱等)
    CLIENT = "client"     # 客户端渠道 (移动端推送等)


def grid_trade_bot_notification_analysis_strategy(content: dict, **kwargs) -> dict:
    """
    方法内容: 网格交易机器人通知内容解析策略，在html解析策略的基础上进行修改
    设计目的: 通过网格交易机器人通知内容解码策略解析通知内容

    Args:
        content (dict): 通知对象的内容，网格交易机器人通知的内容应该包含title和grid_info字典列表，grid_info中的字典包含trade_list和current_change两个列表
        trade_list为可能成交的网格类型详情的id列表,current_change为监控类型可能变化的网格类型详情的id列表

    Returns:
        解析的结果，字典类型，trade_list为买卖数量(buy_count, sell_count)，current_change为网格类型详情监控的变化方式(up/middle/down)
        examples:
             {
               "title":"网格交易确认通知",
               "grid_info":[
                  {
                     "asset_name":"国泰中证全指证券公司ETF",
                     "grid_type_name":"小网",
                     "current_change":"down",
                    "buy_count":0,
                    "sell_count":0
                  },
                  {
                     "asset_name":"易方达中概互联50ETF",
                     "grid_type_name":"小网",
                     "current_change":"down",
                    "buy_count":0,
                    "sell_count":0
                  }
               ]
            }
    """
    content = grid_trade_html_notification_analysis_strategy(content=content, **kwargs)
    for grid_info in content['grid_info']:
        grid_info.update(**grid_info['trade_list'])
        del grid_info['trade_list']
    return content


def grid_trade_html_notification_analysis_strategy(content: dict, **kwargs) -> dict:
    """
    方法内容: 网格交易通知内容解析策略，用于做HTML内容的解析
    设计目的: 通过网格交易通知内容解码策略解析通知内容

    Args:
        content (dict): 通知对象的内容，网格交易通知的内容应该包含title和grid_info字典列表，grid_info中的字典包含trade_list和current_change两个列表
            trade_list为可能成交的网格类型详情的id列表,current_change为监控类型可能变化的网格类型详情的id列表

    Returns:
        解析的结果，字典类型，trade_list为买卖数量(buy_count, sell_count)，current_change为网格类型详情监控的变化方式(up/middle/down)
        examples:
             {
               "title":"网格交易确认通知",
               "grid_info":[
                  {
                     "asset_name":"国泰中证全指证券公司ETF",
                     "grid_type_name":"小网",
                     "trade_list":{
                        "buy_count":0,
                        "sell_count":0
                     },
                     "current_change":"down"
                  },
                  {
                     "asset_name":"易方达中概互联50ETF",
                     "grid_type_name":"小网",
                     "trade_list":{
                        "buy_count":0,
                        "sell_count":0
                     },
                     "current_change":"down"
                  }
               ]
            }
    """
    content_dict: dict = copy.deepcopy(content)
    # 判断通知内容是否包含title和grid_info两个列表对象
    if 'title' not in content_dict or 'grid_info' not in content_dict:
        raise Exception('grid trade notification content error')
    new_grid_infos = []
    # 遍历grid_info列表
    for grid_info in content_dict['grid_info']:
        trade_list = {'buy_count': 0, 'sell_count': 0}
        # 判断trade_list是否存在并且长度大于0
        if 'trade_list' in grid_info and grid_info['trade_list'] is not None and len(grid_info['trade_list']) > 0:
            # 将trade_list反序列化成GridTypeDetail对象列表
            grid_type_details = GridTypeDetailVOSchema(many=True).load(grid_info['trade_list'])
            # 计算trade_list中，监控类型为卖出的网格数量
            buy_count = len([grid_type_detail for grid_type_detail in grid_type_details if
                             grid_type_detail.monitor_type == GridTypeDetail.get_monitor_type_enum().BUY])
            # 计算trade_list中，监控类型为买入的网格数量
            sell_count = len([grid_type_detail for grid_type_detail in grid_type_details if
                              grid_type_detail.monitor_type == GridTypeDetail.get_monitor_type_enum().SELL])
            # 更新trade_count
            trade_list['buy_count'] = buy_count
            trade_list['sell_count'] = sell_count
        # 更新trade_list
        grid_info['trade_list'] = trade_list
        # 判断current_change是否存在
        if 'current_change' in grid_info and grid_info['current_change'] is not None and \
                len(grid_info['current_change']) == 2:
            # 根据current_change获取网格类型详情
            cur_detail: dict = grid_info['current_change'][0]
            now_detail: dict = grid_info['current_change'][1]
            # 判断网格详情监控是往上移还是往下移
            grid_info['current_change'] = 'down' if cur_detail['gear'] > now_detail['gear'] else 'up'
        else:
            grid_info['current_change'] = 'middle'
        new_grid_infos.append(grid_info)
    content_dict['grid_info'] = new_grid_infos
    return content_dict


def grid_trade_client_notification_analysis_strategy(content: dict, **kwargs) -> dict:
    """
    方法内容: 网格交易通知内容解析策略，用于做客户端内容的解析，最终将存入数据库
    设计目的: 通过网格交易通知内容解码策略解析通知内容
    Args:
        content ( dict): 通知对象的内容，网格交易通知的内容应该包含title和grid_info字典列表，grid_info中的字典包含trade_list和current_change两个列表
            trade_list为可能成交的网格类型详情的id列表,current_change为监控类型可能变化的网格类型详情的id列表
        **kwargs ( dict): 其他参数

    Returns:
        解码的结果，字典类型，trade_list和current_change为id对应的实际的网格类型详情数据
    """
    # 判断通知内容是否包含title和grid_info两个列表对象
    if 'title' not in content or 'grid_info' not in content:
        raise Exception('grid trade notification content error')
    # 遍历grid_info列表
    for grid_info in content['grid_info']:
        # 判断trade_list是否存在并且长度大于0
        if 'trade_list' in grid_info and grid_info['trade_list'] is not None and len(grid_info['trade_list']) > 0:
            # 根据trade_list获取网格类型详情，并序列化
            grid_type_details = GridTypeDetail.query.filter(GridTypeDetail.id.in_(grid_info['trade_list'])).all()
            grid_info['trade_list'] = GridTypeDetailVOSchema().dump(grid_type_details, many=True)
        # 判断current_change是否存在
        if 'current_change' in grid_info and grid_info['current_change'] is not None and \
                len(grid_info['current_change']) == 2:
            # 查询第一个网格类型详情
            cur_detail = GridTypeDetail.query.get(grid_info['current_change'][0])
            # 查询第二个网格类型详情
            now_detail = GridTypeDetail.query.get(grid_info['current_change'][1])
            # 更新current_change，序列化网格类型详情列表
            grid_info['current_change'] = GridTypeDetailVOSchema().dump([cur_detail, now_detail], many=True)
    return content


class AnalysisNotificationContentStrategy(ABC):
    """
    分析通知内容策略基类
    """

    @abstractmethod
    def analysis(self, notification: Notification) -> dict:
        """
        分析通知内容
        Args:
            notification (Notification): 通知对象
        Returns:
            dict: 分析后的通知内容
        """
        raise NotImplementedError


class BaseNotificationAnalysisStrategy(AnalysisNotificationContentStrategy):
    """
    基础通知分析策略，提供通用的分析方法
    """
    
    def __init__(self, business_type: BusinessType, channel_type: ChannelType):
        self.business_type = business_type
        self.channel_type = channel_type
    
    def analysis(self, notification: Notification) -> dict:
        """
        通用分析方法，子类可以重写以实现特定逻辑
        """
        debug(f"BaseNotificationAnalysisStrategy analysis notification: {notification.id or 'Unknown'}, "
              f"business_type: {self.business_type.name}, channel_type: {self.channel_type.value}")
        
        try:
            content = json.loads(notification.content or '{}')
        except json.JSONDecodeError as e:
            error(f"Failed to parse notification content: {e}")
            content = {'title': notification.title or '未知标题', 'content': notification.content or ''}
        
        # 基础分析数据结构
        analyzed_data = {
            'title': content.get('title', notification.title or '未知标题'),
            'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S') if notification.timestamp else '未知时间',
            'business_type': self.business_type.value,
            'channel_type': self.channel_type.value,
            'notification_level': notification.notice_level or 0,
            'content': content
        }
        
        return analyzed_data


class GridTradeBotAnalysisStrategy(BaseNotificationAnalysisStrategy):
    """
    网格交易Bot渠道分析策略
    用于解析网格交易通知内容并格式化为Bot消息所需的数据结构
    """
    
    def __init__(self):
        super().__init__(BusinessType.GRID_TRADE, ChannelType.BOT)
    
    def analysis(self, notification: Notification) -> dict:
        """
        分析网格交易通知内容，解析为Bot渲染所需的数据格式
        
        Args:
            notification (Notification): 通知对象
            
        Returns:
            dict: 解析后的通知数据，包含标题和网格信息列表
                格式示例:
                {
                    "title": "网格交易确认通知",
                    "business_type": 0,
                    "channel_type": "bot",
                    "grid_info": [
                        {
                            "asset_name": "国泰中证全指证券公司ETF",
                            "grid_type_name": "小网",
                            "buy_count": 0,
                            "sell_count": 0,
                            "current_change": "down"
                        }
                    ]
                }
        """
        debug(f"GridTradeBotAnalysisStrategy analysis notification: {notification.id or 'Unknown'}")
        
        try:
            content: dict = json.loads(notification.content or '{}')
        except json.JSONDecodeError as e:
            error(f"Failed to parse notification content: {e}")
            return self._create_error_response(notification)
        
        # 提取网格信息
        grid_info: list = content.get('grid_info', [])
        
        # 分析每个网格的交易信息
        analyzed_data: dict = {
            'title': content.get('title', notification.title or '未知标题'),
            'business_type': self.business_type.value,
            'channel_type': self.channel_type.value,
            'grid_info': []
        }
        
        for grid in grid_info:
            grid_analysis: dict = {
                'asset_name': grid.get('asset_name', ''),
                'grid_type_name': grid.get('grid_type_name', ''),
                'buy_count': self._calculate_buy_count(grid.get('trade_list', [])),
                'sell_count': self._calculate_sell_count(grid.get('trade_list', [])),
                'current_change': self._format_current_change(grid.get('current_change', []))
            }
            analyzed_data['grid_info'].append(grid_analysis)
        
        return analyzed_data
    
    def _calculate_buy_count(self, trade_list: list) -> int:
        """
        计算买入交易数量
        
        Args:
            trade_list (list): 交易列表，包含GridTypeDetail对象的字典表示
            
        Returns:
            int: 买入交易数量
        """
        if not trade_list:
            return 0
        
        # 使用GridTypeDetail的监控类型枚举进行判断
        try:
            grid_type_details = GridTypeDetailVOSchema(many=True).load(trade_list)
            return len([detail for detail in grid_type_details 
                       if detail.monitor_type == GridTypeDetail.get_monitor_type_enum().BUY])
        except Exception as e:
            error(f"Failed to load trade_list: {e}")
            return 0
    
    def _calculate_sell_count(self, trade_list: list) -> int:
        """
        计算卖出交易数量
        
        Args:
            trade_list (list): 交易列表，包含GridTypeDetail对象的字典表示
            
        Returns:
            int: 卖出交易数量
        """
        if not trade_list:
            return 0
        
        # 使用GridTypeDetail的监控类型枚举进行判断
        try:
            grid_type_details = GridTypeDetailVOSchema(many=True).load(trade_list)
            return len([detail for detail in grid_type_details 
                       if detail.monitor_type == GridTypeDetail.get_monitor_type_enum().SELL])
        except Exception as e:
            error(f"Failed to load trade_list: {e}")
            return 0
    
    def _format_current_change(self, current_change: list) -> str:
        """
        格式化当前变化信息，根据网格档位变化判断趋势方向
        参考grid_trade_html_notification_analysis_strategy的实现逻辑
        
        Args:
            current_change (list): 当前变化列表，包含两个GridTypeDetail对象的字典表示
                                 [0]为当前详情，[1]为新详情
                                 
        Returns:
            str: 变化方向，可能值为 'up'(上升)、'down'(下降)、'middle'(无变化)
        """
        if not current_change or len(current_change) != 2:
            return 'middle'
        
        try:
            # 根据current_change获取网格类型详情
            cur_detail: dict = current_change[0]  # 当前详情
            now_detail: dict = current_change[1]  # 新详情
            
            # 判断网格详情监控是往上移还是往下移
            # 如果当前档位 > 新档位，说明是下降趋势
            if cur_detail.get('gear', 0) > now_detail.get('gear', 0):
                return 'down'
            elif cur_detail.get('gear', 0) < now_detail.get('gear', 0):
                return 'up'
            else:
                return 'middle'
        except (KeyError, TypeError) as e:
            error(f"Failed to format current_change: {e}")
            return 'middle'
    
    def _create_error_response(self, notification: Notification) -> dict:
        """
        创建错误响应数据结构
        
        Args:
            notification (Notification): 通知对象
            
        Returns:
            dict: 错误响应数据
        """
        return {
            'title': notification.title or '未知标题',
            'business_type': self.business_type.value,
            'channel_type': self.channel_type.value,
            'error': '通知内容解析失败',
            'grid_info': []
        }


class GridTradeHTMLAnalysisStrategy(BaseNotificationAnalysisStrategy):
    """
    网格交易HTML渠道分析策略
    """
    
    def __init__(self):
        super().__init__(BusinessType.GRID_TRADE, ChannelType.HTML)
    
    def analysis(self, notification: Notification) -> dict:
        debug(f"GridTradeHTMLAnalysisStrategy analysis notification: {notification.id or 'Unknown'}")
        
        try:
            content = json.loads(notification.content or '{}')
        except json.JSONDecodeError as e:
            error(f"Failed to parse notification content: {e}")
            return self._create_error_response(notification)
        
        # 为HTML渲染提供更详细的数据结构
        analyzed_data = {
            'title': content.get('title', notification.title or '未知标题'),
            'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S') if notification.timestamp else '未知时间',
            'business_type': self.business_type.value,
            'channel_type': self.channel_type.value,
            'grid_info': []
        }
        
        grid_info = content.get('grid_info', [])
        for grid in grid_info:
            trade_list = grid.get('trade_list', [])
            grid_analysis = {
                'asset_name': grid.get('asset_name', ''),
                'grid_type_name': grid.get('grid_type_name', ''),
                'trade_list': self._format_trade_list_for_html(trade_list),
                'current_change': self._format_current_change_for_html(grid.get('current_change', [])),
                'trade_details': self._format_trade_details(trade_list),
                'current_monitoring': self._format_monitoring_info(grid.get('current_change', [])),
                'statistics': self._calculate_statistics(trade_list)
            }
            analyzed_data['grid_info'].append(grid_analysis)
        
        return analyzed_data
    
    def _format_trade_list_for_html(self, trade_list: list) -> object:
        """
        为HTML模板格式化交易列表，提供buy_count和sell_count属性
        """
        buy_count = sum(1 for trade in trade_list if trade.get('monitorType') == 0)
        sell_count = sum(1 for trade in trade_list if trade.get('monitorType') == 1)
        
        # 创建一个类似对象的字典，支持点号访问
        class TradeListForHTML:
            def __init__(self, buy_count, sell_count):
                self.buy_count = buy_count
                self.sell_count = sell_count
        
        return TradeListForHTML(buy_count, sell_count)
    
    def _format_current_change_for_html(self, current_change: list) -> str:
        """
        为HTML模板格式化当前变化信息
        """
        if not current_change:
            return '无变化'
        
        change = current_change[0]
        change_type = "买入" if change.get('monitorType') == 0 else "卖出"
        return f"{change_type}监控"
    
    def _format_trade_details(self, trade_list: list) -> list:
        """
        格式化交易详情
        """
        formatted_trades = []
        for trade in trade_list:
            formatted_trade = {
                'type': "买入" if trade.get('monitorType') == 0 else "卖出",
                'price': trade.get('purchasePrice' if trade.get('monitorType') == 0 else 'sellPrice', 0) / 1000,
                'shares': trade.get('purchaseShares' if trade.get('monitorType') == 0 else 'sellShares', 0),
                'amount': trade.get('purchaseAmount' if trade.get('monitorType') == 0 else 'sellAmount', 0) / 1000,
                'profit': trade.get('profit', 0) / 1000,
                'gear': trade.get('gear', '')
            }
            formatted_trades.append(formatted_trade)
        return formatted_trades
    
    def _format_monitoring_info(self, current_change: list) -> dict:
        """
        格式化监控信息
        """
        if not current_change:
            return {'status': '无监控变化'}
        
        change = current_change[0]
        return {
            'status': '监控中',
            'type': "买入监控" if change.get('monitorType') == 0 else "卖出监控",
            'trigger_price': change.get('triggerPurchasePrice' if change.get('monitorType') == 0 else 'triggerSellPrice', 0) / 1000,
            'target_price': change.get('purchasePrice' if change.get('monitorType') == 0 else 'sellPrice', 0) / 1000,
            'shares': change.get('purchaseShares' if change.get('monitorType') == 0 else 'sellShares', 0)
        }
    
    def _calculate_statistics(self, trade_list: list) -> dict:
        """
        计算统计信息
        """
        if not trade_list:
            return {'total_trades': 0, 'total_profit': 0, 'avg_profit': 0}
        
        total_profit = sum(trade.get('profit', 0) for trade in trade_list)
        return {
            'total_trades': len(trade_list),
            'total_profit': total_profit / 1000,
            'avg_profit': (total_profit / len(trade_list)) / 1000 if trade_list else 0
        }
    
    def _create_error_response(self, notification: Notification) -> dict:
        """
        创建错误响应
        """
        return {
            'title': notification.title or '未知标题',
            'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S') if notification.timestamp else '未知时间',
            'business_type': self.business_type.value,
            'channel_type': self.channel_type.value,
            'error': '通知内容解析失败',
            'grid_info': []
        }


class GridTradeClientAnalysisStrategy(BaseNotificationAnalysisStrategy):
    """
    网格交易客户端渠道分析策略
    """
    
    def __init__(self):
        super().__init__(BusinessType.GRID_TRADE, ChannelType.CLIENT)
    
    def analysis(self, notification: Notification) -> dict:
        debug(f"GridTradeClientAnalysisStrategy analysis notification: {notification.id or 'Unknown'}")
        
        try:
            content = json.loads(notification.content or '{}')
        except json.JSONDecodeError as e:
            error(f"Failed to parse notification content: {e}")
            return self._create_error_response(notification)
        
        # 客户端通知分析，提供简化的数据结构
        analyzed_data = {
            'title': content.get('title', notification.title or '未知标题'),
            'summary': self._create_summary(content.get('grid_info', [])),
            'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S') if notification.timestamp else '未知时间',
            'business_type': self.business_type.value,
            'channel_type': self.channel_type.value,
            'notification_level': notification.notice_level or 0
        }
        
        return analyzed_data
    
    def _create_summary(self, grid_info: list) -> dict:
        """
        创建摘要信息
        """
        if not grid_info:
            return {'message': '无交易信息'}
        
        total_assets = len(grid_info)
        total_trades = sum(len(grid.get('trade_list', [])) for grid in grid_info)
        
        return {
            'total_assets': total_assets,
            'total_trades': total_trades,
            'message': f"涉及{total_assets}个资产，共{total_trades}笔交易"
        }
    
    def _create_error_response(self, notification: Notification) -> dict:
        """
        创建错误响应
        """
        return {
            'title': notification.title or '未知标题',
            'summary': {'message': '通知内容解析失败'},
            'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S') if notification.timestamp else '未知时间',
            'business_type': self.business_type.value,
            'channel_type': self.channel_type.value,
            'notification_level': notification.notice_level or 0
        }


class NotificationAnalysisStrategyFactory:
    """
    通知分析策略工厂类
    负责根据业务类型和渠道类型创建相应的分析策略
    """
    
    # 策略注册表
    _strategies = {}
    
    @classmethod
    def register_strategy(cls, business_type: BusinessType, channel_type: ChannelType, strategy_class):
        """
        注册策略
        
        Args:
            business_type: 业务类型
            channel_type: 渠道类型
            strategy_class: 策略类
        """
        key = (business_type, channel_type)
        cls._strategies[key] = strategy_class
    
    @classmethod
    def create_strategy(cls, business_type: BusinessType, channel_type: ChannelType) -> BaseNotificationAnalysisStrategy:
        """
        创建策略实例
        
        Args:
            business_type: 业务类型
            channel_type: 渠道类型
            
        Returns:
            BaseNotificationAnalysisStrategy: 策略实例
            
        Raises:
            ValueError: 当找不到对应策略时抛出异常
        """
        key = (business_type, channel_type)
        strategy_class = cls._strategies.get(key)
        
        if strategy_class is None:
            error(f"No strategy found for business_type: {business_type}, channel_type: {channel_type}")
            # 默认使用网格交易Bot策略
            return GridTradeBotAnalysisStrategy()
        
        return strategy_class()
    
    @classmethod
    def get_registered_strategies(cls) -> dict:
        """
        获取所有已注册的策略
        
        Returns:
            dict: 策略注册表
        """
        return cls._strategies.copy()


# 注册所有策略
NotificationAnalysisStrategyFactory.register_strategy(
    BusinessType.GRID_TRADE, ChannelType.BOT, GridTradeBotAnalysisStrategy
)
NotificationAnalysisStrategyFactory.register_strategy(
    BusinessType.GRID_TRADE, ChannelType.HTML, GridTradeHTMLAnalysisStrategy
)
NotificationAnalysisStrategyFactory.register_strategy(
    BusinessType.GRID_TRADE, ChannelType.CLIENT, GridTradeClientAnalysisStrategy
)
NotificationAnalysisStrategyFactory.register_strategy(
    BusinessType.GRID_TRADE, ChannelType.MARKDOWN, GridTradeBotAnalysisStrategy  # 使用Bot策略作为Markdown的默认策略
)

# === 可转债申购策略 ===
class CbSubscribeBotAnalysisStrategy(BaseNotificationAnalysisStrategy):
    def __init__(self):
        super().__init__(BusinessType.CB_SUBSCRIBE, ChannelType.BOT)

    def analysis(self, notification: Notification) -> dict:
        try:
            content = json.loads(notification.content or '{}')
        except json.JSONDecodeError:
            content = {'title': notification.title or '可转债申购提醒', 'items': []}

        items = content.get('items', [])
        normalized = []
        for it in items:
            # 统一字段并格式化日期
            subscribe_date = it.get('subscribe_date')
            if isinstance(subscribe_date, (list, dict)):
                subscribe_date = None
            if hasattr(subscribe_date, 'strftime'):
                subscribe_date = subscribe_date.strftime('%Y-%m-%d')
            normalized.append({
                'bond_name': it.get('bond_name', ''),
                'bond_code': it.get('bond_code', ''),
                'subscribe_date': subscribe_date or '',
                'apply_code': it.get('apply_code', ''),
                'market': it.get('market', ''),
            })

        return {
            'title': content.get('title', notification.title or '可转债申购提醒'),
            'items': normalized
        }


class CbSubscribeHTMLAnalysisStrategy(BaseNotificationAnalysisStrategy):
    def __init__(self):
        super().__init__(BusinessType.CB_SUBSCRIBE, ChannelType.HTML)

    def analysis(self, notification: Notification) -> dict:
        # 复用Bot策略的解析结果，HTML模板层做表格渲染
        bot_strategy = CbSubscribeBotAnalysisStrategy()
        return bot_strategy.analysis(notification)


class DailyReportBotAnalysisStrategy(BaseNotificationAnalysisStrategy):
    def __init__(self):
        super().__init__(BusinessType.DAILY_REPORT, ChannelType.BOT)

    def analysis(self, notification: Notification) -> dict:
        try:
            content = json.loads(notification.content or '{}')
        except json.JSONDecodeError:
            content = {'title': notification.title or '系统每日报告'}

        title = content.get('title', notification.title or '系统每日报告')
        cb_items = content.get('cb_subscribe_tomorrow', []) or []
        test_msg = content.get('databox_test_result', '') or ''
        unprocessed = content.get('unprocessed_confirm_count', 0)
        sched_status = content.get('scheduler_status', '') or ''
        sched_errors = content.get('scheduler_errors_today', []) or []

        # 组装文本模板用的sections结构
        sections = []

        # 明日可转债申购
        cb_lines = []
        for it in cb_items:
            bond_name = it.get('bond_name', '')
            bond_code = it.get('bond_code', '')
            subscribe_date = it.get('subscribe_date', '')
            apply_code = it.get('apply_code', '')
            cb_lines.append(f"{bond_name}({bond_code}) 申购日:{subscribe_date} 申购码:{apply_code}")
        if not cb_lines:
            cb_lines.append('暂无可申购可转债')
        sections.append({'section_title': '明日可转债申购', 'items': cb_lines})

        # DataBox测试结果
        sections.append({'section_title': 'DataBox功能测试', 'items': [test_msg or '未执行测试']})

        # 未处理通知数量
        sections.append({'section_title': '系统通知统计', 'items': [f'未处理确认通知：{unprocessed} 条']})

        # 调度器运行状态
        if sched_status:
            sections.append({'section_title': '调度器状态', 'items': [sched_status]})

        # 当日异常任务
        if sched_errors:
            sections.append({'section_title': '当日异常任务', 'items': sched_errors})
        else:
            sections.append({'section_title': '当日异常任务', 'items': ['今日无异常任务']})

        return {
            'title': title,
            'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S') if notification.timestamp else '',
            'business_type': self.business_type.value,
            'channel_type': self.channel_type.value,
            'notification_level': notification.notice_level or 0,
            'sections': sections
        }


class DailyReportHTMLAnalysisStrategy(BaseNotificationAnalysisStrategy):
    def __init__(self):
        super().__init__(BusinessType.DAILY_REPORT, ChannelType.HTML)

    def analysis(self, notification: Notification) -> dict:
        # 复用Bot策略的解析结果，HTML模板用表格或分段渲染
        bot_strategy = DailyReportBotAnalysisStrategy()
        return bot_strategy.analysis(notification)


NotificationAnalysisStrategyFactory.register_strategy(
    BusinessType.CB_SUBSCRIBE, ChannelType.BOT, CbSubscribeBotAnalysisStrategy
)
NotificationAnalysisStrategyFactory.register_strategy(
    BusinessType.CB_SUBSCRIBE, ChannelType.HTML, CbSubscribeHTMLAnalysisStrategy
)
NotificationAnalysisStrategyFactory.register_strategy(
    BusinessType.CB_SUBSCRIBE, ChannelType.MARKDOWN, CbSubscribeBotAnalysisStrategy
)

# 注册日报策略
NotificationAnalysisStrategyFactory.register_strategy(
    BusinessType.DAILY_REPORT, ChannelType.BOT, DailyReportBotAnalysisStrategy
)
NotificationAnalysisStrategyFactory.register_strategy(
    BusinessType.DAILY_REPORT, ChannelType.HTML, DailyReportHTMLAnalysisStrategy
)

# 为了保持向后兼容，保留原有的策略函数引用
# 这些变量指向上面定义的函数，而不是类实例
# 注意：这些函数引用在AnalysisNotificationContentContext中被使用
# 函数已在文件开头定义，这里创建引用以供AnalysisNotificationContentContext使用
grid_trade_bot_notification_analysis_strategy_func = grid_trade_bot_notification_analysis_strategy
grid_trade_html_notification_analysis_strategy_func = grid_trade_html_notification_analysis_strategy  
grid_trade_client_notification_analysis_strategy_func = grid_trade_client_notification_analysis_strategy


class AnalysisNotificationContentContext:
    """
    解码通知上下文
    """

    def __init__(self, notice_business_type: int = None, strategy=None, channel_type: str = None):
        """
        方法内容: 初始化解码通知上下文，可以通过业务类型使用默认的分析通知策略，也可以通过传入分析通知策略，优先使用传入的分析通知策略
        设计目的: 通过解码通知策略初始化解码通知上下文
        Args:
            notice_business_type (int): 通知业务类型，可以为空，为空时需要传入分析通知策略
            strategy: 解码通知策略，可以为空，为空时需要传入通知业务类型
            channel_type (str): 渠道类型
        """
        # 判断通知业务类型和解码通知策略是否同时为空
        if notice_business_type is None and strategy is None:
            raise Exception('notice business type and strategy is null')
        # 判断解码通知策略是否为空
        if strategy is not None:
            self._analyser = strategy
            return
        
        # 根据业务类型和渠道类型选择策略
        if notice_business_type == 0:  # 网格交易
            if channel_type == "html":
                self._analyser = grid_trade_html_notification_analysis_strategy_func
            elif channel_type == "client":
                self._analyser = grid_trade_client_notification_analysis_strategy_func
            else:
                self._analyser = grid_trade_bot_notification_analysis_strategy_func
        else:
            # 其他业务类型使用默认策略
            self._analyser = grid_trade_html_notification_analysis_strategy_func

    def analysis(self, notification_content: Union[dict, str], **kwargs) -> dict:
        """
        方法内容: 解码通知，调用context初始化的策略方法进行解码
        设计目的: 通过解码通知上下文解码通知
        Args:
            notification_content (Union[dict, str]): 通知对象的内容
            **kwargs: 其他参数

        Returns:

        """
        if isinstance(notification_content, str):
            notification_content = json.loads(notification_content)
        return self._analyser(notification_content, **kwargs)
