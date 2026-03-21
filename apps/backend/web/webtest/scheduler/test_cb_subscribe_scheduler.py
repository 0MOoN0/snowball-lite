#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试可转债申购提醒定时任务：cb_subscribe_today / cb_subscribe_tomorrow

覆盖点：
- 当存在当日/次日申购数据时，会生成通知并走通知发送出口
- 当无数据时，不发送通知
- 通知内容的模板适配（grid_info结构与grid_type_name标签）
"""

import json
from contextlib import nullcontext
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from web.databox.models.dto.convertible_bond_issuance import ConvertibleBondIssuanceData
from web.scheduler.notice_scheduler import cb_subscribe_today, cb_subscribe_tomorrow


class TestCbSubscribeScheduler:

    @pytest.fixture(autouse=True)
    def fake_scheduler_app(self, monkeypatch):
        fake_app = MagicMock()
        fake_app.app_context.return_value = nullcontext()
        monkeypatch.setattr("web.scheduler.notice_scheduler.scheduler.app", fake_app)

    def _make_dto(self, bond_code: str, bond_name: str, d: date) -> ConvertibleBondIssuanceData:
        return ConvertibleBondIssuanceData(
            bond_code=bond_code,
            bond_name=bond_name,
            online_subscribe_date=d,
        )

    @patch('web.scheduler.notice_scheduler.dispatch_notification')
    @patch('web.scheduler.notice_scheduler.notification_service')
    @patch('web.scheduler.notice_scheduler.DataBox.get_cb_issuance_list')
    def test_cb_subscribe_today_send(self, mock_get_list, mock_notice_service, mock_dispatch_notification):
        today = date.today()
        # 构造两条当日申购数据
        dto_list = [
            self._make_dto('123456', '示例转债A', today),
            self._make_dto('654321', '示例转债B', today),
        ]
        mock_get_list.return_value = dto_list

        # 捕获通知对象，验证 helper 接到的内容
        captured = []
        mock_dispatch_notification.side_effect = lambda notification: (captured.append(notification) or True, 'actor')

        # 伪造make_notification以避免DB写入
        def fake_make_notification(business_type, notice_type, content, title):
            from web.models.notice.Notification import Notification
            return Notification(
                id=1,
                business_type=business_type,
                notice_type=notice_type,
                title=title,
                content=json.dumps(content, ensure_ascii=False)
            )

        mock_notice_service.make_notification.side_effect = fake_make_notification

        # 调用定时任务方法
        cb_subscribe_today()

        # 验证发送一次，且内容结构正确
        assert len(captured) == 1
        content = json.loads(captured[0].content)
        assert content.get('title') == '今日可转债申购提醒'
        assert 'grid_info' in content and len(content['grid_info']) == 2
        # grid_type_name 应为“今日申购”标签
        assert all(item.get('grid_type_name') == '今日申购' for item in content['grid_info'])
        # asset_name包含债券简称与代码
        assert any('示例转债A(123456)' == item.get('asset_name') for item in content['grid_info'])
        assert any('示例转债B(654321)' == item.get('asset_name') for item in content['grid_info'])

    @patch('web.scheduler.notice_scheduler.dispatch_notification')
    @patch('web.scheduler.notice_scheduler.notification_service')
    @patch('web.scheduler.notice_scheduler.DataBox.get_cb_issuance_list')
    def test_cb_subscribe_today_no_send_when_empty(self, mock_get_list, mock_notice_service, mock_dispatch_notification):
        # 无数据场景
        mock_get_list.return_value = []

        cb_subscribe_today()

        # 不应投递任何通知
        mock_dispatch_notification.assert_not_called()

    @patch('web.scheduler.notice_scheduler.dispatch_notification')
    @patch('web.scheduler.notice_scheduler.notification_service')
    @patch('web.scheduler.notice_scheduler.DataBox.get_cb_issuance_list')
    def test_cb_subscribe_tomorrow_send(self, mock_get_list, mock_notice_service, mock_dispatch_notification):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        dto_list = [
            self._make_dto('888888', '示例转债C', tomorrow)
        ]
        mock_get_list.return_value = dto_list

        captured = []
        mock_dispatch_notification.side_effect = lambda notification: (captured.append(notification) or True, 'sync')

        def fake_make_notification(business_type, notice_type, content, title):
            from web.models.notice.Notification import Notification
            return Notification(
                id=2,
                business_type=business_type,
                notice_type=notice_type,
                title=title,
                content=json.dumps(content, ensure_ascii=False)
            )

        mock_notice_service.make_notification.side_effect = fake_make_notification

        cb_subscribe_tomorrow()

        assert len(captured) == 1
        content = json.loads(captured[0].content)
        assert content.get('title') == '明日可转债申购提醒'
        assert 'grid_info' in content and len(content['grid_info']) == 1
        # grid_type_name 应为“明日申购”标签
        assert content['grid_info'][0].get('grid_type_name') == '明日申购'
        assert content['grid_info'][0].get('asset_name') == '示例转债C(888888)'

    @patch('web.scheduler.notice_scheduler.dispatch_notification')
    @patch('web.scheduler.notice_scheduler.notification_service')
    @patch('web.scheduler.notice_scheduler.DataBox.get_cb_issuance_list')
    def test_cb_subscribe_tomorrow_no_send_when_mismatch(self, mock_get_list, mock_notice_service, mock_dispatch_notification):
        # 返回非明日数据，过滤后为空
        mock_get_list.return_value = [self._make_dto('999999', '示例转债D', date.today())]

        cb_subscribe_tomorrow()

        mock_dispatch_notification.assert_not_called()

    @patch('web.scheduler.notice_scheduler.dispatch_notification')
    @patch('web.scheduler.notice_scheduler.notification_service')
    def test_cb_subscribe_today_real_call(self, mock_notice_service, mock_dispatch_notification):
        """
        真实调用测试：在环境允许时走 AkShare 真数据。

        条件：
        - 环境变量 RUN_REAL_AKSHARE=1
        - 已安装 akshare 且可访问外网

        验证点：
        - 函数可正常执行，不抛异常
        - 若有数据则投递一条通知并内容结构正确；无数据则不投递
        """
        import os
        try:
            import akshare  # noqa: F401
        except Exception:
            pytest.skip("AkShare is not available in this environment")

        # 捕获通知对象，验证 helper 接到的内容
        captured = []
        mock_dispatch_notification.side_effect = lambda notification: (captured.append(notification) or True, 'actor')

        # 避免DB写入，替换make_notification为纯内存对象
        def fake_make_notification(business_type, notice_type, content, title):
            from web.models.notice.Notification import Notification
            return Notification(
                id=100,
                business_type=business_type,
                notice_type=notice_type,
                title=title,
                content=json.dumps(content, ensure_ascii=False)
            )

        mock_notice_service.make_notification.side_effect = fake_make_notification

        # 调用真实数据流
        cb_subscribe_today()

        # 若捕获到通知，则校验结构；否则认为区间内无申购数据，测试通过
        if captured:
            content = json.loads(captured[0].content)
            assert content.get('title') == '今日可转债申购提醒'
            assert 'grid_info' in content
            assert len(content['grid_info']) > 0
            # 检查首条结构键存在
            first = content['grid_info'][0]
            assert 'asset_name' in first and 'grid_type_name' in first
            assert first.get('grid_type_name') == '今日申购'
        else:
            # 无数据情况下不发送通知
            assert len(captured) == 0

    def test_cb_subscribe_today_manual_no_mock(self):
        """
        手动真实调用：不使用任何mock，直接执行任务函数。

        条件：
        - 建议设置环境变量 RUN_REAL_AKSHARE=1 并安装 akshare，以便获取真实数据

        验证点：
        - 任务函数可直接执行且不抛出异常（不校验外部副作用）
        """
        # 可选地检查akshare存在（不依赖环境变量）
        try:
            import akshare  # noqa: F401
        except Exception:
            pytest.skip("未安装akshare，跳过")

        # 直接执行任务函数，不做任何mock
        try:
            cb_subscribe_today()
        except Exception as e:
            pytest.fail(f"手动执行cb_subscribe_today抛出异常: {e}")

    def test_cb_subscribe_tomorrow_manual_no_mock(self):
        """
        手动真实调用：不使用任何mock，直接执行任务函数（明日提醒）。

        验证点：
        - 任务函数可直接执行且不抛出异常（不校验外部副作用）
        """
        try:
            cb_subscribe_tomorrow()
        except Exception as e:
            pytest.fail(f"手动执行cb_subscribe_tomorrow抛出异常: {e}")
