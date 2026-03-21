import json
import unittest
from datetime import datetime
from pprint import pprint

from web.webtest.BasicRouterTestClass import BasicRouterTestClass


class TestRecordRouters(BasicRouterTestClass):

    def test_put(self):
        # 测试新增
        record = {'date': '2022-01-01', 'code': '123', 'value': 1.01, 'share': 2000, 'fee': 0.2, 'type': 1}
        # record = {}
        res = self.put(url='/irecord', data=record)
        res = json.loads(res.data)
        pprint(res)

    def test_select_by_id(self):
        res = self.get('/irecord/1')
        res = json.loads(res.data)
        pprint(res)


if __name__ == '__main__':
    unittest.main()
