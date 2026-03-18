import unittest
from datetime import datetime
from pprint import pprint

from web.models import db
from web.models.IRecord import IRecord
from web.webtest.TestModelsClass import TestBasicModels


class IRecordTestBasicModels(TestBasicModels):
    @unittest.skip
    def test_save(self):
        session = db.session
        record = IRecord()
        record.trade_date = datetime.now().date()
        record.code = '123'
        record.value = 1.2
        record.share = 1000
        record.fee = 0.2
        record.type = 1
        session.add(record)
        session.commit()

    def test_select(self):
        records = IRecord.query.all()
        pprint(records)


if __name__ == '__main__':
    unittest.main()
