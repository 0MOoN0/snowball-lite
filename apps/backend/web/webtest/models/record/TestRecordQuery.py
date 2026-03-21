# -*- coding: UTF-8 -*-
"""
@File    ：TestRecordQuery.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/10/13 14:51
"""
from test_base import TestBase
from web.models import db
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.record.record import Record


class TestRecordQuery(TestBase):
    def test_record_query(self):
        # 查询Record表和GridTypeRecord连接数据
        # 假设Record有多个字段，这里用column1, column2等表示
        records = db.session.query(Record.column1, Record.column2, ...,
                                   GridTypeRecord.record_id) \
            .join(GridTypeRecord, GridTypeRecord.record_id == Record.id, isouter=True) \
            .order_by(Record.transactions_date.desc()) \
            .paginate(per_page=10, page=1)
        for record in records.items:
            print(record.id)
