#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    ：test_notification_serialization.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025-01-14
@Description: 通知序列化测试
测试NotificationSchema的序列化和反序列化功能
"""

import pytest
import json
from datetime import datetime

from web.models.notice.Notification import Notification, NotificationSchema
from web.webtest.test_base import TestBaseWithRollback


@pytest.mark.usefixtures("rollback_session")
class TestNotificationSerialization(TestBaseWithRollback):
    """
    通知序列化测试类
    
    测试场景：
    1. 通知对象的序列化
    2. 通知对象的反序列化
    3. 序列化后的JSON格式验证
    """
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.test_notification_content = {
            "title": "[序列化测试] 网格交易通知",
            "content": "这是一个序列化测试通知内容",
            "grid_info": [
                {
                    "asset_name": "测试ETF基金",
                    "trade_list": [
                        {
                            "trade_type": "买入",
                            "amount": 1000,
                            "price": 1.5
                        }
                    ]
                }
            ]
        }
        
    def create_test_notification(self, rollback_session):
        """创建测试通知对象"""
        notification = Notification(
            title="[序列化测试] 通知序列化测试",
            content=json.dumps(self.test_notification_content),
            notice_level=0,
            business_type=Notification.get_business_type_enum().GRID_TRADE.value,
            notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value,
            notice_status=Notification.get_notice_status_enum().NOT_SENT.value,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        rollback_session.add(notification)
        rollback_session.commit()
        return notification
    
    def test_notification_schema_dumps(self, rollback_session):
        """
        测试通知对象序列化为JSON字符串
        """
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        print(f"创建的通知ID: {notification.id}")
        print(f"通知标题: {notification.title}")
        
        # 序列化为JSON字符串
        try:
            notification_json = NotificationSchema().dumps(notification)
            print(f"序列化成功，JSON长度: {len(notification_json)}")
            print(f"JSON内容: {notification_json[:200]}...")
            
            # 验证JSON格式
            parsed_json = json.loads(notification_json)
            assert isinstance(parsed_json, dict)
            assert 'id' in parsed_json
            assert 'title' in parsed_json
            
            print("序列化测试通过")
            
        except Exception as e:
            print(f"序列化失败: {e}")
            raise
    
    def test_notification_schema_loads(self, rollback_session):
        """
        测试JSON字符串反序列化为通知对象
        """
        # 创建测试通知并序列化
        notification = self.create_test_notification(rollback_session)
        notification_json = NotificationSchema().dumps(notification)
        
        print(f"原始通知ID: {notification.id}")
        
        # 反序列化
        try:
            deserialized_notification = NotificationSchema().loads(notification_json)
            print(f"反序列化成功")
            print(f"反序列化后的通知ID: {deserialized_notification.id}")
            print(f"反序列化后的标题: {deserialized_notification.title}")
            
            # 验证反序列化结果
            assert isinstance(deserialized_notification, Notification)
            assert deserialized_notification.id == notification.id
            assert deserialized_notification.title == notification.title
            
            print("反序列化测试通过")
            
        except Exception as e:
            print(f"反序列化失败: {e}")
            raise
    
    def test_notification_schema_round_trip(self, rollback_session):
        """
        测试序列化和反序列化的完整流程
        """
        # 创建测试通知
        original_notification = self.create_test_notification(rollback_session)
        
        print(f"原始通知: ID={original_notification.id}, 标题={original_notification.title}")
        
        # 序列化
        notification_json = NotificationSchema().dumps(original_notification)
        print(f"序列化完成，JSON长度: {len(notification_json)}")
        
        # 反序列化
        restored_notification = NotificationSchema().loads(notification_json)
        print(f"反序列化完成: ID={restored_notification.id}, 标题={restored_notification.title}")
        
        # 验证数据一致性
        assert restored_notification.id == original_notification.id
        assert restored_notification.title == original_notification.title
        assert restored_notification.content == original_notification.content
        assert restored_notification.business_type == original_notification.business_type
        assert restored_notification.notice_type == original_notification.notice_type
        assert restored_notification.notice_status == original_notification.notice_status
        
        print("完整流程测试通过")