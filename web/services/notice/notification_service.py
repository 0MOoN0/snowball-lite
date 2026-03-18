# -*- coding: utf-8 -*-

import json
from typing import List

from web.decorator import singleton
from web.models import db
from web.models.notice.Notification import Notification
from web.services.notice.analyser.notification_analyser import AnalysisNotificationContentContext, \
    grid_trade_client_notification_analysis_strategy
from web.services.notice.notification_config_service import notification_config_service
from web.services.notice.sender.sender_strategy import SenderContext
from web.services.notice.sender.strategy_factory import sender_strategy_factory
from web.weblogger import debug, error


@singleton
class NotificationService:

    def __init__(self):
        # 移除硬编码策略，改为动态获取
        self.config_service = notification_config_service
        self.strategy_factory = sender_strategy_factory

    def make_notification(self, business_type: int, notice_type: int, content: dict, title: str) -> Notification:
        """
        方法内容: 生成通知对象，并储存到数据库中
        设计目的，方便生成通知对象，未来可以将其封装成统一的通知生成接口
        Args:
            business_type (int): 通知的业务类型，比如日志、系统等
            notice_type (int):  通知的类型，0-消息型通知，1-确认型通知 
            content (dict): 通知的内容
            title (str): 通知标题

        Returns:
            Notification: 通知对象
        """
        notification = Notification()
        notification.business_type = business_type
        notification.notice_type = notice_type
        # 根据业务类型决定是否进行客户端侧的内容预处理
        try:
            from web.common.enum.NotificationEnum import NotificationBusinessTypeEnum as BizEnum
            if business_type == BizEnum.GRID_TRADE.value:
                analysis_context = AnalysisNotificationContentContext(
                    strategy=grid_trade_client_notification_analysis_strategy)
                notification.content = json.dumps(analysis_context.analysis(notification_content=content),
                                                  ensure_ascii=False)
            else:
                # 其他业务类型保持原始内容，交由渲染层进行分析
                notification.content = json.dumps(content, ensure_ascii=False)
        except Exception:
            # 兜底：保存原始内容
            notification.content = json.dumps(content, ensure_ascii=False)
        notification.title = title
        with db.session.no_autoflush:
            db.session.add(notification)
            db.session.flush()
            db.session.commit()
        return notification

    def get_sender_contexts_for_business(self, business_type: int) -> List[SenderContext]:
        """
        根据业务类型获取发送上下文列表（支持多渠道发送）
        
        Args:
            business_type (int): 业务类型
            
        Returns:
            List[SenderContext]: 发送上下文列表
        """
        try:
            # 将业务类型转换为字符串
            business_type_str = self._convert_business_type_to_string(business_type)

            # 根据业务类型获取通知渠道列表
            channels = self.config_service.get_channels_for_business(business_type_str)

            # 过滤启用的渠道
            enabled_channels = []
            for channel in channels:
                if self.config_service.is_channel_enabled(channel):
                    enabled_channels.append(channel)
                else:
                    debug(f"渠道 {channel} 未启用，跳过")

            # 如果没有启用的渠道，使用默认渠道
            if not enabled_channels:
                debug("没有启用的渠道，使用默认渠道")
                default_channel = self.config_service.get_default_channel()
                enabled_channels = [default_channel]

            # 创建发送上下文列表
            sender_contexts = []
            for channel in enabled_channels:
                try:
                    sender_context = self.strategy_factory.create_context(channel)
                    sender_contexts.append(sender_context)
                except Exception as e:
                    error(f"创建渠道 {channel} 的发送上下文失败: {str(e)}")

            debug(f"为业务类型 {business_type_str} 选择通知渠道: {enabled_channels}")

            return sender_contexts

        except Exception as e:
            error(f"获取发送上下文失败，使用默认渠道: {str(e)}")
            # 发生错误时使用默认渠道
            default_channel = self.config_service.get_default_channel()
            return [self.strategy_factory.create_context(default_channel)]

    def get_sender_context_for_business(self, business_type: int) -> SenderContext:
        """
        根据业务类型获取第一个发送上下文（向后兼容方法）
        
        Args:
            business_type (int): 业务类型
            
        Returns:
            SenderContext: 发送上下文
        """
        sender_contexts = self.get_sender_contexts_for_business(business_type)
        return sender_contexts[0] if sender_contexts else None

    def _convert_business_type_to_string(self, business_type: int) -> str:
        """
        将业务类型整数转换为字符串
        
        Args:
            business_type (int): 业务类型整数
            
        Returns:
            str: 业务类型字符串（与数据库中的键名格式匹配）
        """
        # 与枚举保持一致：0-网格交易,1-消息提醒,2-系统运行,3-日报,4-可转债申购
        if business_type == 0:
            return "grid_trade"
        elif business_type == 1:
            return "message_remind"
        elif business_type == 2:
            return "system_runing"
        elif business_type == 3:
            return "daily_report"
        elif business_type == 4:
            return "cb_subscribe"
        else:
            return "grid_trade"

    def send_notification(self, notification: Notification) -> bool:
        """
        发送通知（支持多渠道发送）
        
        Args:
            notification (Notification): 通知对象
            
        Returns:
            bool: 是否至少有一个渠道发送成功
        """
        result = self.send_notification_with_retry(notification)
        return result['success']

    def send_notification_with_retry(self, notification: Notification, max_retry: int = 3,
                                     failure_callback=None) -> dict:
        """
        发送通知（支持多渠道发送和重试机制）
        
        Args:
            notification (Notification): 通知对象
            max_retry (int): 每个渠道的最大重试次数
            failure_callback (callable): 失败回调函数，接收参数(channel_index, error)
            
        Returns:
            dict: {
                'success_count': int,
                'total_count': int, 
                'failed_channels': list,
                'success': bool
            }
        """
        try:
            # 获取发送上下文列表
            sender_contexts = self.get_sender_contexts_for_business(notification.business_type)

            # 记录发送结果
            success_count = 0
            total_count = len(sender_contexts)
            failed_channels = []

            # 通过所有渠道发送通知
            for i, sender_context in enumerate(sender_contexts):
                channel_success = False
                send_times = 0
                last_error = None

                # 尝试通过当前渠道发送（带重试）
                while send_times <= max_retry and not channel_success:
                    try:
                        sender_context.send(notification)
                        channel_success = True
                        success_count += 1
                        debug(f"通知通过渠道 {i + 1} 发送成功: {notification.title}")
                        break
                    except Exception as e:
                        send_times += 1
                        last_error = e

                        if failure_callback:
                            failure_callback(i, e)

                        if send_times <= max_retry:
                            debug(f"渠道 {i + 1} 发送失败，第 {send_times} 次重试: {str(e)}")
                        else:
                            error(f"渠道 {i + 1} 发送失败，已达到最大重试次数: {str(e)}", exc_info=True)

                if not channel_success:
                    failed_channels.append({
                        'channel_index': i,
                        'error': str(last_error) if last_error else 'Unknown error'
                    })

            # 返回详细结果
            result = {
                'success_count': success_count,
                'total_count': total_count,
                'failed_channels': failed_channels,
                'success': success_count > 0
            }

            if result['success']:
                debug(f"通知发送完成: {notification.title}, 成功 {success_count}/{total_count} 个渠道")
            else:
                error(f"通知发送失败: {notification.title}, 所有渠道都失败")

            return result

        except Exception as e:
            error(f"通知发送失败: {notification.title}, 错误: {str(e)}")
            return {
                'success_count': 0,
                'total_count': 0,
                'failed_channels': [{'channel_index': -1, 'error': str(e)}],
                'success': False
            }


notification_service: NotificationService = NotificationService()
