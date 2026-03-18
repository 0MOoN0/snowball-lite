from web.models.task.Task import Task


class TaskItem:
    """
    任务，任务队列的负载
    task : 任务对象
    payload : 任务附带的数据，仅存在于内存中，无持久化处理
    """

    def __init__(self, task: Task, payload=None):
        self.task = task
        self.payload = payload
