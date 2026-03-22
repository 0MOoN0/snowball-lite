from abc import ABC, abstractmethod

import os
from abc import ABC, abstractmethod

from jinja2 import Environment, FileSystemLoader

from web.models.notice.Notification import Notification
from web.services.notice.analyser.notification_analyser import (
    BusinessType,
    ChannelType,
    NotificationAnalysisStrategyFactory,
)
from web.services.notice.render.template_resolver import TemplateResolver
from web.web_exception.WebException import NotificationRenderException
from web.weblogger import error


class NotificationRenderStrategy(ABC):
    """
    通知渲染策略
    """

    def __init__(self, autoescape: bool):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建到 web/template 的相对路径
        # 从 'services/notice/render' 返回三级到 'web'，然后进入 'template'
        self.template_dir = os.path.join(current_dir, "..", "..", "..", "template")
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir), autoescape=autoescape
        )
        # 集成模板解析器
        self.template_resolver = TemplateResolver(self.template_dir)

    def get_template_path(self, notification: Notification, render_type: str) -> str:
        """
        获取模板路径，支持动态模板选择

        Args:
            notification: 通知对象
            render_type: 渲染类型 (bot/html)

        Returns:
            str: 模板路径
        """
        return self.template_resolver.resolve_template_path(
            business_type=notification.business_type,
            render_type=render_type,
            template_key=notification.template_key,
        )

    @abstractmethod
    def render(self, notification: Notification, **kwargs):
        pass


class ServerChenRenderStrategy(NotificationRenderStrategy):
    """
    Server酱渲染策略
    """

    def __init__(self):
        # 调用父类初始化，确保template_resolver等属性正确初始化
        super().__init__(autoescape=False)

    def render(self, notification: Notification, **kwargs) -> str:
        """
        渲染通知内容
        Args:
            notification (Notification): 通知对象
            **kwargs: 其他参数
        Returns:
            str: 渲染后的通知内容
        """
        # 根据业务类型和渠道类型创建分析器
        try:
            business_type = BusinessType(notification.business_type)
        except ValueError:
            error(
                f"Unknown business type: {notification.business_type}, using GRID_TRADE as default"
            )
            business_type = BusinessType.GRID_TRADE

        # 使用新的策略工厂创建分析器
        analysis_strategy = NotificationAnalysisStrategyFactory.create_strategy(
            business_type, ChannelType.BOT
        )
        # 使用策略实例的analysis方法，得到完整模板上下文
        analyzed_data = analysis_strategy.analysis(notification)

        try:
            # 使用模板解析器获取模板路径
            template_path = self.get_template_path(notification, "bot")
            template = self.jinja_env.get_template(template_path)
            # 透传分析输出，避免固定字段绑定
            rendered_content = template.render(**analyzed_data)
        except Exception as e:
            error(f"ServerChen通知内容渲染错误: {e}")
            raise NotificationRenderException(msg="ServerChen通知内容渲染错误")

        return rendered_content


class NotificationBotRenderStrategy(NotificationRenderStrategy):
    """
    通知Bot渲染策略
    """

    def __init__(self):
        super().__init__(autoescape=False)  # autoescape 通常对text是False

    def render(self, notification: Notification, **kwargs) -> str:
        """
        方法内容: 渲染通知为Bot消息
        设计目的: 使用内容分析器解析通知，并渲染为Bot消息
        Args:
            notification (Notification): 通知对象
            **kwargs (dict): 其他参数

        Returns: 格式化后的通知内容，案例：
            📢 网格交易确认通知 📢

            资产名称:国泰中证全指证券公司ETF
            网格类型:小网
            当前变化:down
            买入数:0
            卖出数:0

            资产名称:易方达中概互联50ETF
            网格类型:小网
            当前变化:down
            买入数:0
            卖出数:0

        """
        # 根据业务类型和渠道类型创建分析器
        try:
            business_type = BusinessType(notification.business_type)
        except ValueError:
            error(
                f"Unknown business type: {notification.business_type}, using GRID_TRADE as default"
            )
            business_type = BusinessType.GRID_TRADE

        # 使用新的策略工厂创建分析器
        analysis_strategy = NotificationAnalysisStrategyFactory.create_strategy(
            business_type, ChannelType.BOT
        )
        # 使用策略实例的analysis方法，得到完整模板上下文
        parsed_content: dict = analysis_strategy.analysis(notification)

        try:
            # 使用动态模板路径解析
            template_path = self.get_template_path(notification, "bot")
            template = self.jinja_env.get_template(template_path)
            # 透传分析输出字典，让不同业务的模板自行取字段
            rendered_text = template.render(**parsed_content)
        except Exception as e:
            error(f"通知内容Bot模板渲染错误: {e}")
            raise NotificationRenderException(msg="通知内容Bot模板渲染错误")

        return rendered_text


class NotificationHTMLRenderStrategy(NotificationRenderStrategy):
    """
    通知HTML渲染策略
    """

    def __init__(self):
        super().__init__(autoescape=True)

    def render(self, notification: Notification, **kwargs) -> str:
        """
        方法内容: 渲染通知为HTML
        设计目的: 通过通知渲染策略渲染通知为HTML
        Args:
            notification (Notification): 通知对象
            **kwargs (dict): 其他参数

        Returns:
            str: 渲染后的HTML内容
        """
        # 根据业务类型和渠道类型创建分析器
        try:
            business_type = BusinessType(notification.business_type)
        except ValueError:
            error(
                f"Unknown business type: {notification.business_type}, using GRID_TRADE as default"
            )
            business_type = BusinessType.GRID_TRADE

        # 使用新的策略工厂创建分析器
        analysis_strategy = NotificationAnalysisStrategyFactory.create_strategy(
            business_type, ChannelType.HTML
        )
        # 使用策略实例的analysis方法，得到完整模板上下文
        content: dict = analysis_strategy.analysis(notification)

        try:
            # 使用动态模板路径解析
            template_path = self.get_template_path(notification, "html")
            template = self.jinja_env.get_template(template_path)
            # 透传分析输出字典，HTML模板可按各业务字段渲染
            html_content = template.render(**content)
        except Exception as e:
            # 记录日志内容
            error(f"通知内容Jinja2渲染错误: {e}")
            # 抛出格式化错误异常
            raise NotificationRenderException(msg="通知内容Jinja2渲染错误")
        return html_content


class NotificationContentRenderContext:
    """
    通知渲染上下文
    """

    def __init__(self, render_strategy: NotificationRenderStrategy):
        """
        方法内容: 初始化通知渲染上下文
        设计目的: 通过通知渲染策略初始化通知渲染上下文
        Args:
            render_strategy (NotificationRenderStrategy): 通知渲染策略
        """
        self.render_strategy = render_strategy

    def render(self, notification: Notification, **kwargs) -> str:
        """
        方法内容: 渲染通知
        设计目的: 通过通知渲染上下文渲染通知
        Args:
            notification (Notification): 通知对象
            **kwargs: 其他参数

        Returns:

        """
        return self.render_strategy.render(notification, **kwargs)
