from datetime import date, datetime, timedelta
from typing import List, Union
import random

from web.common.utils.timezone_util import parse_to_date
from web.databox.data_box import DataBox
from web.databox.models.dto.convertible_bond_issuance import ConvertibleBondIssuanceData
from web.decorator.scheduler_timeout import scheduler_timeout
from web.models.notice.Notification import Notification
from web.models import db
from web.scheduler.base import scheduler
from web.scheduler.notification_dispatch import dispatch_notification
from web.services.notice.builders.cb_subscribe_builder import make_cb_subscribe_content
from web.services.notice.notification_service import (
    NotificationService,
    notification_service,
)
from web.models.scheduler.scheduler_log import SchedulerLog
from sqlalchemy import func, or_
from web.weblogger import logger

mod_logger = logger.getChild(__name__)


@scheduler.task(id='notice_scheduler.cb_subscribe_today', name='可转债申购提醒-今日（08:30）', trigger='cron', hour=8, minute=30, misfire_grace_time=60 * 15, coalesce=False)
@scheduler_timeout(60, '可转债申购提醒-今日任务超时')
def cb_subscribe_today(start: Union[date, str] = None, end: Union[date, str] = None):
    """
    定时任务：提醒当天可转债网上申购。
    通过 DataBox 获取近 30 天的发行列表，筛选 `online_subscribe_date == 今天` 的记录并发送通知。
    """
    with scheduler.app.app_context():
        mod_logger.info('定时任务开始: 可转债申购提醒-今日(08:30)')
        today: date = date.today()

        # 解析自定义时间窗口（可选）
        start_date = parse_to_date(start, today - timedelta(days=30))
        end_date = parse_to_date(end, today + timedelta(days=1))
        databox = DataBox()
        try:
            issuance_list = databox.get_cb_issuance_list(start_date=start_date, end_date=end_date)
            mod_logger.info(f"[cb_subscribe_today] 发行列表获取成功: total={len(issuance_list)}")
            today_items = [dto for dto in issuance_list if dto.online_subscribe_date == today]
            mod_logger.info(f"[cb_subscribe_today] 今日可申购数量: {len(today_items)}")
        except Exception:
            mod_logger.error('[cb_subscribe_today] 获取发行列表失败', exc_info=True)
            today_items = []

        if today_items:
            notification_content = make_cb_subscribe_content(items=today_items, title='今日可转债申购提醒', tag='今日申购')

            notice_service: NotificationService = notification_service
            notification = notice_service.make_notification(
                business_type=Notification.get_business_type_enum().CB_SUBSCRIBE.value,
                notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value,
                content=notification_content,
                title='今日可转债申购提醒',
            )
            sent, channel = dispatch_notification(notification)
            if sent:
                if channel == "actor":
                    mod_logger.info('[cb_subscribe_today] Actor发送成功')
                else:
                    mod_logger.info('[cb_subscribe_today] 同步发送成功')
            else:
                mod_logger.error('[cb_subscribe_today] 通知发送失败')
        else:
            mod_logger.info('[cb_subscribe_today] 今日无可申购项目，跳过通知')
        mod_logger.info('定时任务结束: 可转债申购提醒-今日(08:30)')


@scheduler.task(id='notice_scheduler.cb_subscribe_tomorrow', name='可转债申购提醒-明日（20:00）', trigger='cron', hour=20, minute=0)
@scheduler_timeout(60, '可转债申购提醒-明日任务超时')
def cb_subscribe_tomorrow(start: Union[date, str] = None, end: Union[date, str] = None):
    """
    定时任务：提醒次日可转债网上申购。
    通过 DataBox 获取近 30 天的发行列表，筛选 `online_subscribe_date == 明天` 的记录并发送通知。
    """
    with scheduler.app.app_context():
        mod_logger.info('定时任务开始: 可转债申购提醒-明日(20:00)')
        today: date = date.today()
        tomorrow: date = today + timedelta(days=1)

        start_date = parse_to_date(start, today - timedelta(days=30))
        end_date = parse_to_date(end, tomorrow + timedelta(days=1))
        databox = DataBox()
        try:
            issuance_list = databox.get_cb_issuance_list(start_date=start_date, end_date=end_date)
            tomorrow_items = [dto for dto in issuance_list if dto.online_subscribe_date == tomorrow]
            mod_logger.info(f"[cb_subscribe_tomorrow] 明日申购计算完成: total={len(issuance_list)}, tomorrow={len(tomorrow_items)}")
        except Exception:
            mod_logger.error('[cb_subscribe_tomorrow] 获取发行列表失败', exc_info=True)
            tomorrow_items = []

        if tomorrow_items:
            notification_content = make_cb_subscribe_content(items=tomorrow_items, title='明日可转债申购提醒', tag='明日申购')

            notice_service: NotificationService = notification_service
            notification = notice_service.make_notification(
                business_type=Notification.get_business_type_enum().CB_SUBSCRIBE.value,
                notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value,
                content=notification_content,
                title='明日可转债申购提醒',
            )
            sent, channel = dispatch_notification(notification)
            if sent:
                if channel == "actor":
                    mod_logger.info('[cb_subscribe_tomorrow] Actor发送成功')
                else:
                    mod_logger.info('[cb_subscribe_tomorrow] 同步发送成功')
            else:
                mod_logger.error('[cb_subscribe_tomorrow] 通知发送失败')
        else:
            mod_logger.info('[cb_subscribe_tomorrow] 明日无可申购项目，跳过通知')
        mod_logger.info('定时任务结束: 可转债申购提醒-明日(20:00)')


@scheduler.task(id='notice_scheduler.daily_report', name='系统每日报告（20:00）', trigger='cron', hour=20, minute=0)
@scheduler_timeout(60, '系统每日报告任务超时')
def daily_report(start: Union[date, str] = None, end: Union[date, str] = None):
    """
    定时任务：系统每日报告（20:00）。
    当前内容包含：
    - 明天可申购可转债（参考 cb_subscribe_tomorrow 逻辑）
    - DataBox get_rt 功能测试结果（参考 databox_test_scheduler.test_databox_get_rt）
    - 未处理的确认型通知数量

    未来可扩展包含当天收益率等内容。
    """
    with scheduler.app.app_context():
        mod_logger.info('定时任务开始: 系统每日报告(20:00)')
        today: date = date.today()
        tomorrow: date = today + timedelta(days=1)


        # 1) 明日可转债申购情况
        try:
            start_date = parse_to_date(start, today - timedelta(days=30))
            end_date = parse_to_date(end, tomorrow + timedelta(days=1))
            databox = DataBox()
            issuance_list = databox.get_cb_issuance_list(start_date=start_date, end_date=end_date)
            tomorrow_items = [dto for dto in issuance_list if dto.online_subscribe_date == tomorrow]
            mod_logger.info(f"[daily_report] 明日申购计算完成: total={len(issuance_list)}, tomorrow={len(tomorrow_items)}")
        except Exception:
            mod_logger.error('[daily_report] 获取发行列表失败', exc_info=True)
            tomorrow_items = []

        if tomorrow_items:
            cb_content = make_cb_subscribe_content(items=tomorrow_items, title='明日可转债申购提醒', tag='明日申购')
            cb_items = cb_content.get('items', [])
        else:
            cb_items = []

        # 2) DataBox get_rt 功能测试结果（简化：固定代码，不输出异常详细信息）
        test_result_msg = ''
        try:
            test_code = 'SZ162411'
            rt = DataBox().get_rt(test_code)
            if rt is None:
                test_result_msg = '失败(SZ162411)'
            else:
                test_result_msg = '成功(SZ162411)'
        except Exception:
            test_result_msg = '失败(SZ162411)'
        mod_logger.info(f"[daily_report] DataBox get_rt 测试结果: {test_result_msg}")

        # 保留 test_result_msg 供模板渲染使用

        # 3) 未处理的确认型通知数量（排除未发送）
        try:
            status_enum = Notification.get_notice_status_enum()
            # 统计已发送但未处理的确认型通知：包含未读/已读/已发送，排除未发送与已处理
            valid_statuses = [
                status_enum.NOT_READ.value,
                status_enum.READ.value,
                status_enum.SENT.value,
            ]
            unprocessed_count = db.session.query(Notification) \
                .filter(Notification.notice_type == Notification.get_notice_type_enum().CONFIRM_MESSAGE.value) \
                .filter(Notification.notice_status.in_(valid_statuses)) \
                .count()
        except Exception:
            unprocessed_count = 0
        mod_logger.info(f"[daily_report] 未处理确认通知数量: {unprocessed_count}")

        # 保留 unprocessed_count 供模板渲染使用

        # 4) 调度器运行状态与当日异常任务
        try:
            running = False
            if hasattr(scheduler, '_scheduler'):
                running = bool(getattr(scheduler._scheduler, 'running', False))
            elif hasattr(scheduler, 'running'):
                running = bool(getattr(scheduler, 'running', False))
        except Exception:
            running = False
        mod_logger.info(f"[daily_report] 调度器状态: {'运行' if running else '未运行/异常'}")

        # 构建job映射用于友好展示
        job_map = {}
        try:
            for job in scheduler.get_jobs() or []:
                job_map[getattr(job, 'id', None)] = getattr(job, 'name', None)
        except Exception:
            pass
        mod_logger.debug(f"[daily_report] 当前注册任务数: {len(job_map)}")

        # 查询最近24小时异常任务（按预计运行时间）
        try:
            error_state = SchedulerLog.get_scheduler_state_enum().ERROR.value
            miss_state = SchedulerLog.get_scheduler_state_enum().MISSED.value
            # 使用最近24小时的半开区间时间窗口，避免等值比较与时区误差
            window_end = datetime.now()
            window_start = window_end - timedelta(hours=24)
            mod_logger.debug(f"[daily_report] 异常日志时间窗口(24h): {window_start} ~ {window_end}")
            error_logs = db.session.query(SchedulerLog) \
                .filter(or_(SchedulerLog.execution_state == error_state, SchedulerLog.execution_state == miss_state)) \
                .filter(SchedulerLog.scheduler_run_time >= window_start) \
                .filter(SchedulerLog.scheduler_run_time < window_end) \
                .order_by(SchedulerLog.scheduler_run_time.desc()) \
                .limit(20).all()
        except Exception:
            error_logs = []
        mod_logger.info(f"[daily_report] 当日异常任务数量: {len(error_logs)}")

        # 格式化异常任务列表（带异常类型标签：执行异常/错过执行）
        errors_today = []
        for log in error_logs:
            job_id = getattr(log, 'job_id', '')
            job_name = job_map.get(job_id) or job_id
            run_time = getattr(log, 'scheduler_run_time', None)
            run_time_str = run_time.strftime('%H:%M:%S') if run_time else ''
            state = getattr(log, 'execution_state', None)
            state_label = '执行异常' if state == error_state else ('错过执行' if state == miss_state else '未知状态')
            errors_today.append(f"[{state_label}] {job_name} ({job_id}) @ {run_time_str}")
        for line in errors_today:
            mod_logger.debug(f"[daily_report] 异常任务: {line}")

        # 生成并发送日报通知
        notice_service: NotificationService = notification_service
        content = {
            'title': '系统每日报告',
            'cb_subscribe_tomorrow': cb_items,
            'databox_test_result': test_result_msg,
            'unprocessed_confirm_count': unprocessed_count,
            'scheduler_status': '运行正常' if running else '未运行/异常',
            'scheduler_errors_today': errors_today
        }
        notification = notice_service.make_notification(
            business_type=Notification.get_business_type_enum().DAILY_REPORT.value,
            notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value,
            content=content,
            title='系统每日报告'
        )
        sent, channel = dispatch_notification(notification)
        if sent:
            if channel == "actor":
                mod_logger.info('[daily_report] Actor发送成功')
            else:
                mod_logger.info('[daily_report] 同步发送成功')
        else:
            mod_logger.error('[daily_report] 通知发送失败')
        mod_logger.info('定时任务结束: 系统每日报告(20:00)')
