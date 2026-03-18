import numbers
import queue
import string
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from sqlalchemy import and_

from web.common.enum.TaskEnum import TaskStatusEnum
from web.decorator import singleton
from web.web_exception import WebBaseException
from web.models import db
from web.models.asset.asset_code import AssetCode
from web.models.task.Task import Task
from web.models.task.TaskAsset import TaskAsset
from web.models.task.TaskLog import TaskLog
from web.task.TaskModel import TaskItem
from web.task.TaskService import task_service
from web.weblogger import logger


@singleton
class TaskManager:
    """
    任务管理器，已经废弃，使用Dramatiq代替
    """

    def __init__(self, running=False):
        if running:
            self.block_queue = queue.Queue(maxsize=10000)
            self.execute_flag: bool = True
            self.thread_pool = ThreadPoolExecutor(max_workers=1)
            self.task = None
            self.app = None

    def put(self, item: TaskItem) -> bool:
        """
        将给定任务添加到队列，被添加进队列的任务状态会从”未执行“修改为”等待执行“，当任务状态不为”未执行时“会返回False，说明任务可能已经在队列中或
        正在执行
        Args:
            item (TaskItem):任务对象

        Returns:
            添加操作是否成功，如果未添加进队列，或者任务状态修改失败时，返回False
        """
        # 修改任务状态
        with db.session.no_autoflush as session:
            res = item.task.query \
                .filter(and_(Task.id == item.task.id, Task.task_status == TaskStatusEnum.NOT_EXECUTED.value)) \
                .update({Task.task_status: TaskStatusEnum.WAITING.value})
        if res <= 0:
            logger.error('task id : %s 任务状态异常，该任务可能已经存在队列中或正在执行中' % item.task.id)
            raise WebBaseException(msg='任务状态与预期不符')
        if self.block_queue.full():
            logger.error('任务队列已满，请检查')
            raise WebBaseException(msg='Task queue is full')
        session.commit()
        self.block_queue.put(item)
        return res > 0

    def qsize(self):
        return self.block_queue.qsize()

    def start(self, app):
        self.app = app
        self.task = self.thread_pool.submit(self._do_start)
        return True

    def _do_start(self):
        while self.execute_flag:
            task_item: TaskItem = self.block_queue.get(block=True)
            # app = current_app._get_current_object()
            with self.app.app_context():
                with db.session.no_autoflush as session:
                    # 修改任务状态为执行中
                    status_res = task_item.task.query \
                        .filter(and_(Task.id == task_item.task.id, Task.task_status == TaskStatusEnum.WAITING.value)) \
                        .update({Task.task_status: TaskStatusEnum.EXECUTING.value})
                    session.flush()
                    # 如果任务状态修改失败，可能是有其他地方修改了任务状态，此时跳过执行该任务，避免任务重复执行
                    if status_res <= 0:
                        logger.error(
                            'task id : %s 任务状态异常，该任务可能已经存在队列中或正在执行中' % task_item.task.id)
                        continue
                    execute_result = False
                    remark = ''
                    try:
                        start = datetime.now()
                        execute_result = task_service.execute(task_item)
                        end = datetime.now()
                    except Exception as e:
                        logger.error('task id : %s 任务状态异常，异常信息:%s' % (task_item.task.id, e))
                        end = datetime.now()
                        remark = str(e)
                    time_consuming = (start - end).microseconds
                    # 记录执行日志
                    task_log = self._get_task_log(task_item, execute_result, time_consuming, remark)
                    session.add(task_log)
                    # 将任务状态从执行中修改为已执行
                    status_res = task_item.task.query \
                        .filter(and_(Task.id == task_item.task.id, Task.task_status == TaskStatusEnum.EXECUTING.value)) \
                        .update(
                        {Task.task_status: TaskStatusEnum.EXECUTED.value, Task.time_consuming: time_consuming})
                    if status_res <= 0:
                        logger.error(
                            'task id : %s 任务状态异常，该任务可能已经存在队列中或正在执行中' % task_item.task.id)
                session.commit()
            self.block_queue.task_done()

    def close(self):
        self.execute_flag = False
        return True

    def _get_task_log(self, task_item: TaskItem, execute_result: bool, time_consuming: numbers, remark: string):
        asset_code: AssetCode = db.session.query(AssetCode) \
            .join(TaskAsset, and_(AssetCode.asset_id == TaskAsset.asset_id), isouter=True) \
            .filter(TaskAsset.task_id == task_item.task.id) \
            .first()
        task_log = TaskLog()
        task_log.asset_id = asset_code.asset_id
        task_log.task_id = task_item.task.id
        task_log.execute_time = datetime.now()
        task_log.business_type = task_item.task.business_type
        task_log.time_consuming = time_consuming
        task_log.execute_result = execute_result
        task_log.remark = remark
        return task_log


task_manager = TaskManager()
