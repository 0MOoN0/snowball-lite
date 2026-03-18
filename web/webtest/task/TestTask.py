from web.models.notice.Notification import NotificationSchema
from web.webtest.test_base import TestBase


class TestTask(TestBase):

    def test_send_notification(self):
        """
        测试发送通知
        Returns:

        """
        from web.services.notice.notification_service import notification_service
        notification = notification_service.make_notification(0, 0, {'title': 'test', 'grid_info': []}, title='test')
        from web.task.actors.NotificationActors import send_notification
        send_notification.send(NotificationSchema().dump(notification))


    def test_notification_actors(self):
        """
        测试通知actor
        Returns:
        """
        # 查询第一个通知
        from web.models.notice.Notification import Notification
        notification = Notification.query.first()
        from web.task.actors import NotificationActors
        notice_dump = NotificationSchema().dumps(notification)
        NotificationActors.send_notification.send(notice_dump)


