from web.models.task.Task import Task
from web.task.TaskManager import TaskItem
from web.task.TaskService import task_service
from web.webtest.BasicRouterTestClass import BasicRouterTestClass


class TaskServiceTest(BasicRouterTestClass):
    def test_execute(self):
        task = Task()
        item = TaskItem(task)
        item.task.id = 1
        task_service.execute(item)
