import json
from datetime import datetime
from unittest.mock import MagicMock, patch

from flask import Flask

from web.models.notice.Notification import Notification, NotificationSchema
from web.scheduler.notification_dispatch import dispatch_notification


class TestNotificationDispatch:

    def _make_notification(self) -> Notification:
        return Notification(
            id=1001,
            business_type=Notification.get_business_type_enum().SYSTEM_RUNNING.value,
            notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value,
            notice_status=Notification.get_notice_status_enum().NOT_SENT.value,
            title="调度测试通知",
            content=json.dumps({
                "title": "调度测试通知",
                "content": "fallback 测试",
            }, ensure_ascii=False),
            notice_level=1,
            timestamp=datetime.now(),
        )

    @patch('web.scheduler.notification_dispatch.notification_service')
    @patch('web.scheduler.notification_dispatch.NotificationActors.send_notification')
    def test_dispatch_notification_actor_success(self, mock_actor, mock_notification_service):
        notification = self._make_notification()
        mock_actor.send = MagicMock()

        result = dispatch_notification(notification)

        assert result == (True, 'actor')
        mock_actor.send.assert_called_once()
        mock_notification_service.send_notification.assert_not_called()

        payload = mock_actor.send.call_args[0][0]
        sent_notification = NotificationSchema().loads(payload)
        assert sent_notification.title == notification.title
        assert sent_notification.content == notification.content

    @patch('web.scheduler.notification_dispatch.notification_service')
    @patch('web.scheduler.notification_dispatch.NotificationActors.send_notification')
    def test_dispatch_notification_actor_failure_fallback_sync(self, mock_actor, mock_notification_service):
        notification = self._make_notification()
        mock_actor.send = MagicMock(side_effect=RuntimeError('queue down'))
        mock_notification_service.send_notification.return_value = True

        result = dispatch_notification(notification)

        assert result == (True, 'sync')
        mock_actor.send.assert_called_once()
        mock_notification_service.send_notification.assert_called_once_with(notification)

    @patch('web.scheduler.notification_dispatch.notification_service')
    @patch('web.scheduler.notification_dispatch.NotificationActors.send_notification')
    def test_dispatch_notification_both_fail(self, mock_actor, mock_notification_service):
        notification = self._make_notification()
        mock_actor.send = MagicMock(side_effect=RuntimeError('queue down'))
        mock_notification_service.send_notification.side_effect = RuntimeError('sync down')

        result = dispatch_notification(notification)

        assert result == (False, 'failed')
        mock_actor.send.assert_called_once()
        mock_notification_service.send_notification.assert_called_once_with(notification)

    @patch('web.scheduler.notification_dispatch.notification_service')
    @patch('web.scheduler.notification_dispatch.NotificationActors.send_notification')
    def test_dispatch_notification_skip_actor_when_task_queue_unavailable(self, mock_actor, mock_notification_service):
        notification = self._make_notification()
        app = Flask(__name__)
        app.config['TASK_QUEUE_AVAILABLE'] = False
        mock_notification_service.send_notification.return_value = True

        with app.app_context():
            result = dispatch_notification(notification)

        assert result == (True, 'sync')
        mock_actor.send.assert_not_called()
        mock_notification_service.send_notification.assert_called_once_with(notification)
