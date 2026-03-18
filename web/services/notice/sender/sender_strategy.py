# -*- coding: UTF-8 -*-
"""
@File    ：sender_strategy.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/9/16 23:25
"""
import asyncio
import json
from abc import ABC, abstractmethod

import requests
from telegram import Bot

from web.decorator import singleton
from web.models.notice.Notification import Notification
from web.services.notice.notification_config_service import notification_config_service
from web.services.notice.render.notification_render import (
    NotificationContentRenderContext,
    ServerChenRenderStrategy,
    NotificationBotRenderStrategy,
    NotificationHTMLRenderStrategy,
)
from web.weblogger import debug, error


class SenderStrategy(ABC):
    """
    发送策略
    """

    @abstractmethod
    def send(self, notification: Notification, **kwargs):
        # 抛出实现异常
        raise NotImplementedError


class ServerChenSenderStrategy(SenderStrategy):
    """
    Server酱发送策略类
    """

    def send(self, notification: Notification, **kwargs):
        """
        方法内容: 发送通知
        设计目的: 通过Server酱接口发送通知
        Args:
            notification (Notification): 通知对象
            **kwargs: 其他参数
        Returns:

        """
        # 从数据库配置中获取sendkey
        sendkey = notification_config_service.get_setting_by_key("notification_sender.server_chan")
        if sendkey is None or sendkey.strip() == "":
            raise Exception('Server酱 sendkey 配置为空，请在系统设置中配置 notification_sender.server_chan')
        # 使用渲染策略渲染通知内容
        context = NotificationContentRenderContext(render_strategy=ServerChenRenderStrategy())
        content: str = context.render(notification)
        # 使用markdown格式发送消息
        self.do_send(sendkey=sendkey, title=notification.title, content=content)

    def do_send(self, sendkey, title, content):
        try:
            # 使用 post 和 请求体发送
            response = requests.post(url='https://sctapi.ftqq.com/{}.send'.format(sendkey),
                                     data={'text': title, 'desp': content})
            if response.status_code == 200:
                result = response.json()
                if not result['data']['errno'] == 0:
                    error(f"Server酱推送失败: {result}", exc_info=True)
                    raise Exception(f"Server酱推送失败: {result}")
                else:
                    debug("Server酱推送成功")
            else:
                error_msg = f"Server酱推送请求失败, 状态码: {response.status_code}"
                error(error_msg)
                raise Exception(error_msg)
        except requests.RequestException as e:
            # 捕获requests库抛出的所有异常
            error(f"Server酱推送过程中发生异常: {e}", exc_info=True)
            raise Exception(f"Server酱推送过程中发生异常: {e}")


class TelegramBotSenderStrategy(SenderStrategy):
    """
    TelegramBot发送策略类
    """

    def send(self, notification: Notification, **kwargs):
        """
        方法内容: 发送通知
        设计目的: 通过TelegramBot接口发送通知
        Args:
            notification (Notification): 通知对象
            **kwargs: 其他参数
        Returns:

        """
        # 从数据库配置中获取token和chat_id
        telegram_config = notification_config_service.get_setting_by_key("notification_sender.telegram_bot")
        if telegram_config is None or telegram_config.strip() == "":
            raise Exception('Telegram Bot 配置为空，请在系统设置中配置 notification_sender.telegram_bot')
        
        # 解析JSON格式配置：{"token": "xxx", "chat_id": "xxx"}
        try:
            config_data = json.loads(telegram_config)
            token = config_data.get('token')
            chat_id = config_data.get('chat_id')
        except json.JSONDecodeError as e:
            raise Exception(f'Telegram Bot 配置JSON格式错误: {str(e)}')
        
        if not token or not chat_id:
            raise Exception('Telegram Bot token 或 chat_id 配置为空')
        # 使用渲染策略渲染通知内容
        context = NotificationContentRenderContext(render_strategy=NotificationBotRenderStrategy())
        content: str = context.render(notification)
        return asyncio.run(self.do_send(token, chat_id, content))

    async def do_send(self, token, chat_id, message):
        """
        方法内容: 发送消息，注意可能会有连接错误的问题
        Args:
            token:
            chat_id:
            message:

        Returns:

        """
        bot: Bot = Bot(token=token)
        res = await bot.send_message(chat_id=chat_id, text=message)
        return res


@singleton
class PushPlusSenderStrategy(SenderStrategy):
    """
    PushPlus发送策略类
    """

    def send(self, notification: Notification, **kwargs):
        """
        方法内容: 发送通知
        设计目的: 通过PushPlus接口发送通知
        Args:
            notification (Notification): 通知对象
            **kwargs: 其他参数

        Returns:

        """
        # 从数据库配置中获取pushplus token
        token = notification_config_service.get_setting_by_key("notification_sender.pushplus")
        if token is None or token.strip() == "":
            raise Exception('PushPlus token 配置为空，请在系统设置中配置 notification_sender.pushplus')
        
        source_content: dict = json.loads(notification.content)
        # 构建url为http://www.pushplus.plus/send的post请求,请求参数为token、title、content、template
        render_context = NotificationContentRenderContext(NotificationHTMLRenderStrategy())
        content = render_context.render(notification)
        post_body = {
            'token': token,
            'title': source_content['title'],
            'content': content,
        }
        debug('send notification to push plus, content: {}'.format(content))
        post_res = requests.post('http://www.pushplus.plus/send', post_body)
        # 如果请求失败，抛出异常
        if post_res.status_code != 200:
            raise Exception('push plus sender send error')


@singleton
class WeComSenderStrategy(SenderStrategy):
    """
    企业微信发送策略类
    """

    def send(self, notification: Notification, **kwargs):
        """
        方法内容: 发送通知
        设计目的: 通过企业微信接口发送通知
        Args:
            notification (Notification): 通知对象
            **kwargs: 其他参数

        Returns:

        """
        # 从数据库配置中获取企业微信webhook key
        webhook_key = notification_config_service.get_setting_by_key("notification_sender.wecom")
        if webhook_key is None or webhook_key.strip() == "":
            raise Exception('企业微信 webhook key 配置为空，请在系统设置中配置 notification_sender.wecom')
        
        # 构建完整的企业微信webhook URL
        webhook_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
        
        # 使用渲染策略渲染通知内容
        context = NotificationContentRenderContext(render_strategy=NotificationBotRenderStrategy())
        content: str = context.render(notification)
        
        # 构建企业微信消息格式
        post_body = {
            "msgtype": "text",
            "text": {
                # 由模板负责渲染标题，避免重复标题导致视觉拥挤
                "content": content
            }
        }
        
        debug('send notification to wecom, content: {}'.format(post_body))
        
        try:
            post_res = requests.post(webhook_url, json=post_body)
            if post_res.status_code == 200:
                result = post_res.json()
                if result.get('errcode') == 0:
                    debug("企业微信推送成功")
                else:
                    error(f"企业微信推送失败: {result}")
                    raise Exception(f"企业微信推送失败: {result}")
            else:
                error_msg = f"企业微信推送请求失败, 状态码: {post_res.status_code}"
                error(error_msg)
                raise Exception(error_msg)
        except requests.RequestException as e:
            error(f"企业微信推送过程中发生异常: {e}", exc_info=True)
            raise Exception(f"企业微信推送过程中发生异常: {e}")


class SenderContext:
    """
    发送上下文
    """

    def __init__(self, sender_strategy: SenderStrategy):
        """
        方法内容: 初始化发送上下文
        设计目的: 通过发送策略初始化发送上下文
        Args:
            sender_strategy (SenderStrategy): 发送策略
        """
        self.sender_strategy = sender_strategy

    def send(self, notification: Notification, sender_strategy: SenderStrategy = None, **kwargs):
        """
        方法内容: 发送通知
        设计目的: 通过发送上下文发送通知
        Args:
            sender_strategy: 发送策略，使用什么方式发送，api接口，bot等等。
            notification (Notification): 通知对象
            **kwargs: 其他参数

        Returns:

        """
        if sender_strategy is not None:
            sender_strategy.send(notification, **kwargs)
        else:
            self.sender_strategy.send(notification, **kwargs)
