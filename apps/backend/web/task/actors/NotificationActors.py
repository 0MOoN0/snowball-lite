from datetime import datetime

from web.weblogger import debug, error
from web.common.cons import webcons
from web.models import db
from web.models.notice.Notification import NotificationSchema, Notification
from web.models.notice.notification_log import NotificationLog
from web.services.notice.notification_service import notification_service
from web.task import dramatiq
from datetime import datetime
import traceback


@dramatiq.actor(queue_name=webcons.NOTIFICATION_QUEUE_NAME)
def send_notification(notification: str):
    """
    发送通知（使用notification_service进行多渠道发送）
    设计目的：方便发送通知，支持全局重试机制
    Args:
        notification (str): 字符串格式的通知对象
    """
    debug('进入通知发送方法')
    notification: Notification = NotificationSchema().loads(notification)
    debug('获取到通知对象,id:{}'.format(notification.id))
    
    # 定义失败回调函数，用于记录渠道级别的失败日志
    def channel_failure_callback(channel_index, error):
        try:
            traceback_info = traceback.format_exc()
            notice_log = NotificationLog(
                notification_id=notification.id, 
                traceback_info=f'渠道{channel_index+1}发送失败: {traceback_info}'
            )
            db.session.add(notice_log)
            db.session.commit()
        except Exception as log_error:
            error(f'记录通知日志失败: {str(log_error)}', exc_info=True)
    
    try:
        # 使用notification_service的增强发送方法（包含渠道级重试）
        result = notification_service.send_notification_with_retry(
            notification, 
            max_retry=3,  # 每个渠道重试3次
            failure_callback=channel_failure_callback
        )
        
        # 记录发送结果
        debug(f'通知发送结果: 成功 {result["success_count"]}/{result["total_count"]} 个渠道')
        
        # 检查是否至少有一个渠道发送成功
        if result['success']:
            # 通过数据库查询获取通知对象并更新状态
            db_notification = db.session.query(Notification).filter(Notification.id == notification.id).first()
            if db_notification:
                db_notification.notice_status = Notification.get_notice_status_enum().NOT_READ.value
                db_notification.timestamp = datetime.now()
                db.session.commit()
            debug('通知发送成功')
        else:
            # 所有渠道都失败，检查是否需要全局延时重试
            log_times = db.session.query(NotificationLog).filter(
                NotificationLog.notification_id == notification.id).count()
            if log_times < webcons.NOTIFICATION_GLOBAL_MAX_RETRY:
                error('所有渠道发送失败，进行全局延时重试', exc_info=True)
                send_notification.send_with_options(
                    args=(NotificationSchema().dumps(notification),),
                    delay=webcons.NOTIFICATION_RETRY_DELAY
                )
            else:
                error('所有渠道发送失败，已达到全局最大重试次数，停止发送', exc_info=True)
            
    except Exception as e:
        error(f'通知发送异常: {str(e)}', exc_info=True)
        # 记录异常日志
        try:
            traceback_info = traceback.format_exc()
            notice_log = NotificationLog(
                notification_id=notification.id, 
                traceback_info=f'全局发送异常: {traceback_info}'
            )
            db.session.add(notice_log)
            db.session.commit()
        except Exception as log_error:
            error(f'记录异常日志失败: {str(log_error)}', exc_info=True)
