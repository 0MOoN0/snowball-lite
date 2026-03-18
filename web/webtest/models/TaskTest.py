from datetime import time

from web.common.enum.TaskEnum import TaskStatusEnum
from web.models import db
from web.models.task.Task import Task
from web.task.TaskManager import task_manager
from web.task.TaskModel import TaskItem
from web.webtest.TestModelsClass import TestBasicModels


class TaskTestBasicModels(TestBasicModels):

    def test_add_to_manager(self):
        task = Task.query.filter(Task.id == 9)
        task.task_status = TaskStatusEnum.NOT_EXECUTED.value
        db.session.commit()
        task_item = TaskItem(task=task)
        task_manager.put(task_item)
        time.sleep(100000)
