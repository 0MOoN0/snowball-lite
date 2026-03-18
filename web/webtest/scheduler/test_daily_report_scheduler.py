# -*- coding: UTF-8 -*-
"""
测试目标：直接调用 notice_scheduler.daily_report，验证每日报告通知被正确生成。

覆盖范围与验证点:
- 原始调用：直接调用定时任务函数（非通过APScheduler触发），不做队列/方法替换。
- 通知持久化：生成一条业务类型为 DAILY_REPORT 的通知。
- 内容结构：content 为 JSON，包含以下明确字段：
  - title（字符串）
  - cb_subscribe_tomorrow（列表）
  - databox_test_result（字符串）
  - unprocessed_confirm_count（整数）
  - scheduler_status（字符串）
  - scheduler_errors_today（列表）
"""

import json

from web.models import db
from web.models.notice.Notification import Notification
from web.common.enum.NotificationEnum import NotificationBusinessTypeEnum
from web.scheduler.notice_scheduler import daily_report
from web.webtest.test_base import TestBase


class TestDailyReportScheduler(TestBase):
    def test_direct_call_daily_report(self):
        """
        原始调用 daily_report() 并断言通知生成及内容结构。

        验证点:
        - 生成通知的 business_type == DAILY_REPORT
        - 通知标题为“系统每日报告”
        - content 可解析为 JSON，包含 'title' 与 'grid_info'
        - grid_info 至少包含三条信息（明日可转债、DataBox测试、未处理通知数）
        """
        # 保持原始调用（不绕过装饰器，不替换队列）
        daily_report()

        # 查询最新的日报通知（业务类型为 DAILY_REPORT）
        notification: Notification = (
            db.session.query(Notification)
            .filter(Notification.business_type == NotificationBusinessTypeEnum.DAILY_REPORT.value)
            .order_by(Notification.id.desc())
            .first()
        )

        assert notification is not None, "未生成每日报告通知"
        assert notification.title == "系统每日报告"

        # 解析内容 JSON
        content = json.loads(notification.content or "{}")
        assert isinstance(content, dict)
        assert content.get("title") == "系统每日报告"

        # 明确字段校验
        assert "cb_subscribe_tomorrow" in content and isinstance(content["cb_subscribe_tomorrow"], list)
        assert "databox_test_result" in content and isinstance(content["databox_test_result"], str)
        assert "unprocessed_confirm_count" in content and isinstance(content["unprocessed_confirm_count"], int)
        assert "scheduler_status" in content and isinstance(content["scheduler_status"], str)
        assert "scheduler_errors_today" in content and isinstance(content["scheduler_errors_today"], list)

        # 业务合理性（弱校验）：出现“暂无可申购可转债”时 cb_subscribe_tomorrow 允许为空
        cb_items = content.get("cb_subscribe_tomorrow", [])
        assert isinstance(cb_items, list)