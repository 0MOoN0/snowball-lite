import json
from datetime import datetime

from web.databox import databox
from web.models import db
from web.models.notice.Notification import Notification
from web.scheduler.base import scheduler
from web.scheduler.notification_dispatch import dispatch_notification
from web.weblogger import error, info


@scheduler.task(
    id="DataboxTestScheduler.test_databox_get_rt",
    name="DataBox get_rt功能测试（每天下午4点）",
    trigger="cron",
    hour=16,
    minute=0,
    misfire_grace_time=60 * 10,
)
def test_databox_get_rt():
    """
    定时任务：测试 databox.get_rt 是否可用
    执行时间：每天下午4点
    功能：使用固定代码测试 DataBox 的实时数据获取（与 daily_report 保持一致）
    固定代码：SZ162411（国泰中证全指证券公司ETF）
    失败处理：如果测试失败，构建消息型通知并走通知发送出口
    """
    with scheduler.app.app_context():
        info("开始执行 DataBox get_rt 功能测试任务")

        test_code = "SZ162411"
        try:
            info(f"使用固定测试代码: {test_code}")
            result = databox.get_rt(test_code)

            if result is None:
                error(f"DataBox get_rt 测试失败，代码: {test_code}，返回结果为 None")
                _send_test_failure_notification(
                    f"DataBox get_rt 测试失败，测试代码: {test_code}，返回结果为 None"
                )
            else:
                info(
                    f"DataBox get_rt 测试成功，代码: {test_code}，获取到数据: {getattr(result, 'name', '数据正常')}"
                )

        except Exception as e:
            error(f"DataBox get_rt 测试过程中发生异常: {str(e)}", exc_info=True)
            _send_test_failure_notification(f"DataBox get_rt 测试过程中发生异常: {str(e)}")


def _send_test_failure_notification(error_message: str):
    """
    发送测试失败通知

    Args:
        error_message (str): 错误信息
    """
    try:
        # 构建通知对象
        notification = Notification(
            business_type=Notification.get_business_type_enum().SYSTEM_RUNNING.value,
            notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value,
            notice_status=Notification.get_notice_status_enum().NOT_SENT.value,
            title="DataBox功能测试失败",
            content=json.dumps({
                "test_type": "databox_get_rt_test",
                "test_result": "failure",
                "error_message": error_message,
                "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "description": "DataBox get_rt功能测试失败"
            }, ensure_ascii=False),
            notice_level=1,  # 设置为中等重要性
            timestamp=datetime.now(),
        )

        # 保存通知到数据库
        db.session.add(notification)
        db.session.commit()

        # 通知发送失败时也不能影响整个 scheduler 任务
        sent, channel = dispatch_notification(notification)
        if sent:
            if channel == "actor":
                info(f"已通过Actor发送DataBox测试失败通知，通知ID: {notification.id}")
            else:
                info(f"已通过同步方式发送DataBox测试失败通知，通知ID: {notification.id}")
        else:
            error(f"DataBox测试失败通知发送失败，通知ID: {notification.id}")

    except Exception as e:
        error(f"发送测试失败通知时发生异常: {str(e)}", exc_info=True)
