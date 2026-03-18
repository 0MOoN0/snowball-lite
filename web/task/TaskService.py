from web.task.TaskManager import TaskItem
from web.task.TaskStrategy import task_context


class TaskService:
    @classmethod
    def execute(cls, task_item: TaskItem) -> bool:
        return task_context.execute(task_item)


task_service = TaskService()
