import json
import unittest
from pprint import pprint

from flask import jsonify

from web import create_app
from web.common.cons import webcons
from web.models import db
from web.models.Menu import Menu
from web.models.grid.GridTypeDetail import GridTypeDetail



class TestApp(unittest.TestCase):
    """
    已废弃！
    """

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client()

    #
    # def test_config(self):
    #     # self.assertIsNotNone(self.app.config['TESTING'])
    #     self.assertEqual(self.app.config['TESTING'], True)

    # def test_helloworld(self):
    #     result = self.client.get('/')
    #     self.assertEqual(result.get_data(as_text=True), 'helloworld')
    @unittest.skip
    def test_404(self):
        result = self.client.get('/test')
        pprint(jsonify(result))

    # 数据库查询测试
    @unittest.skip
    def test_select_db(self):
        grids = GridTypeDetail.query.all()
        self.assertIsNotNone(grids)

    # 数据库插入测试 @unittest.skip：跳过测试用例
    @unittest.skip
    def test_insert_db(self):
        menu = Menu()
        menu.path = '/test'
        db.session.add(menu)
        db.session.commit()




if __name__ == '__main__':
    suit = unittest.TestSuite()
    suit.addTest(TestApp('test_404'))

    runner = unittest.TextTestRunner()
    runner.run(suit)
