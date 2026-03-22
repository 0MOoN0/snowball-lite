import json
from datetime import datetime
from unittest.mock import patch

from flask import Flask

from web.models.notice.Notification import Notification, NotificationSchema
from web.scheduler.notification_dispatch import dispatch_notification


class TestNotificationDispatch:
    def _make_app(self, task_queue_available: bool) -> Flask:
        app = Flask(__name__)
        app.config["TASK_QUEUE_AVAILABLE"] = task_queue_available
        app.config["ENABLE_TASK_QUEUE"] = task_queue_available
        return app

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
    @patch('web.scheduler.notification_dispatch._send_notification_via_actor')
    def test_dispatch_notification_actor_success(self, mock_actor, mock_notification_service):
        notification = self._make_notification()
        app = self._make_app(task_queue_available=True)

        with app.app_context():
            result = dispatch_notification(notification)

        assert result == (True, 'actor')
        mock_actor.assert_called_once()
        mock_notification_service.send_notification.assert_not_called()

        payload = mock_actor.call_args[0][0]
        sent_notification = NotificationSchema().loads(payload)
        assert sent_notification.title == notification.title
        assert sent_notification.content == notification.content

    @patch('web.scheduler.notification_dispatch.notification_service')
    @patch('web.scheduler.notification_dispatch._send_notification_via_actor')
    def test_dispatch_notification_actor_failure_fallback_sync(self, mock_actor, mock_notification_service):
        notification = self._make_notification()
        app = self._make_app(task_queue_available=True)
        mock_actor.side_effect = RuntimeError('queue down')
        mock_notification_service.send_notification.return_value = True

        with app.app_context():
            result = dispatch_notification(notification)

        assert result == (True, 'sync')
        mock_actor.assert_called_once()
        mock_notification_service.send_notification.assert_called_once_with(notification)

    @patch('web.scheduler.notification_dispatch.notification_service')
    @patch('web.scheduler.notification_dispatch._send_notification_via_actor')
    def test_dispatch_notification_both_fail(self, mock_actor, mock_notification_service):
        notification = self._make_notification()
        app = self._make_app(task_queue_available=True)
        mock_actor.side_effect = RuntimeError('queue down')
        mock_notification_service.send_notification.side_effect = RuntimeError('sync down')

        with app.app_context():
            result = dispatch_notification(notification)

        assert result == (False, 'failed')
        mock_actor.assert_called_once()
        mock_notification_service.send_notification.assert_called_once_with(notification)

    @patch('web.scheduler.notification_dispatch.notification_service')
    @patch('web.scheduler.notification_dispatch._send_notification_via_actor')
    def test_dispatch_notification_skip_actor_when_task_queue_unavailable(self, mock_actor, mock_notification_service):
        notification = self._make_notification()
        app = self._make_app(task_queue_available=False)
        mock_notification_service.send_notification.return_value = True

        with app.app_context():
            result = dispatch_notification(notification)

        assert result == (True, 'sync')
        mock_actor.assert_not_called()
        mock_notification_service.send_notification.assert_called_once_with(notification)
