import pytest
from sqlalchemy import or_

from web.models.notice.Notification import Notification


@pytest.mark.usefixtures("app")
class TestNotification:
    def test_union_select(self):
        # 获取指定id的通知
        notification_id: int = 135
        notification: Notification = Notification.query.get(notification_id)
        exist_unprocessed_notification: Notification = Notification.query.filter(
            or_(Notification.notice_status == Notification.get_notice_status_enum().NOT_READ.value,
                Notification.notice_status == Notification.get_notice_status_enum().READ.value),
            Notification.business_type == Notification.get_business_type_enum().GRID_TRADE.value,
            Notification.timestamp < notification.timestamp).count() > 0
        self.assertTrue(exist_unprocessed_notification)

