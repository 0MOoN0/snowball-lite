# -*- coding: UTF-8 -*-
"""
@File    ：TestNotificationRenderStrategy.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/9/15 20:38
"""
import pytest # 导入 pytest
from test_base import TestBase
from web.models.notice.Notification import Notification
from web.services.notice.render.notification_render import NotificationBotRenderStrategy, NotificationHTMLRenderStrategy
import json # 导入 json 模块

@pytest.mark.usefixtures("rollback_session") # 应用 rollback_session fixture
class TestNotificationRenderStrategy(TestBase):
    def test_bot_render_strategy(self, rollback_session): # 注入 rollback_session
        # 查询第一个通知
        notice = Notification.query.with_session(rollback_session).first()
        if not notice: # 如果没有通知，创建一个模拟的通知对象用于测试
            # 构造符合预期的 content JSON 字符串
            content_data = {
                "title": "机器人网格交易确认通知",
                "grid_info": [
                    {
                        "asset_name": "国泰中证全指证券公司ETF",
                        "grid_type_name": "小网",
                        "trade_list": [], # 假设没有交易发生
                        "current_change": [] # 假设没有价格档位变化
                    }
                ]
            }
            notice = Notification(
                title="Test Bot Notification",
                content=json.dumps(content_data), # 将字典转换为 JSON 字符串
                notice_level=0, 
                business_type=Notification.get_business_type_enum().GRID_TRADE.value, 
                notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value 
            )
            rollback_session.add(notice)
            rollback_session.flush() 

        strategy = NotificationBotRenderStrategy()
        content = strategy.render(notice)
        print("Rendered Bot Content:")
        print(content)
        assert isinstance(content, str) # 修改为 assert isinstance
        assert "机器人网格交易确认通知" in content # 修改为 assert ... in

    def test_html_render_strategy(self, rollback_session): # 注入 rollback_session
        # 查询第一个通知
        notice = Notification.query.with_session(rollback_session).first()
        # 如果没有通知，可以创建一个模拟的通知对象用于测试
        if not notice:
            content_data = {
                "title": "HTML网格交易确认通知",
                "grid_info": [
                    {
                        "asset_name": "易方达中概互联50ETF",
                        "grid_type_name": "大网",
                        "trade_list": [], # 假设没有交易发生
                        "current_change": [] # 假设没有价格档位变化
                    }
                ]
            }
            notice = Notification(
                title="Test HTML Notification",
                content=json.dumps(content_data), # 将字典转换为 JSON 字符串
                notice_level=0, 
                business_type=Notification.get_business_type_enum().GRID_TRADE.value, 
                notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value 
            )
            rollback_session.add(notice)
            rollback_session.flush()

        strategy = NotificationHTMLRenderStrategy()
        html_content = strategy.render(notice)
        print("Rendered HTML Content:")
        print(html_content)
        assert isinstance(html_content, str) # 修改为 assert isinstance
        assert "HTML网格交易确认通知" in html_content # 修改为 assert ... in
        assert "易方达中概互联50ETF" in html_content # 修改为 assert ... in
