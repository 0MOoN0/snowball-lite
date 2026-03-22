import json
import unittest

from web import create_app
from web.models import db


class BasicRouterTestClass(unittest.TestCase):
    """
    unittest.TestCase 已废弃
    """


    def setUp(self) -> None:
        self.app = create_app(config_name='dev')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def put(self, url='', data={}):
        return self.client.put(url, data=json.dumps(data), content_type='application/json')

    def get(self, url='', params={}):
        return self.client.get(url, data=params)
