from sqlalchemy import func

from web.models import db
from web.models.scheduler.scheduler_log import SchedulerLog
from web.webtest.test_base import TestBase


class TestSchedulerLog(TestBase):
    def test_union_select(self):
        success_query = db.session.query(SchedulerLog.job_id, func.count(SchedulerLog.id).label('success_count')) \
            .filter(SchedulerLog.execution_state == SchedulerLog.get_scheduler_state_enum().EXECUTED) \
            .group_by(SchedulerLog.job_id)
        fail_query = db.session.query(SchedulerLog.job_id, func.count(SchedulerLog.id).label('fail_count')) \
            .filter(SchedulerLog.execution_state == SchedulerLog.get_scheduler_state_enum().ERROR) \
            .group_by(SchedulerLog.job_id)
        res = success_query.union(fail_query).all()