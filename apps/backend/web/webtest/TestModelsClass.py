import pytest

from web import create_app
from web.models import db


@pytest.mark.usefixtures("client", "session")
class TestBasicModels:
    """
    已经废弃！
    基础模型测试类，使用测试数据库，自动创建和删除相关数据
    """

    def setUp(self) -> None:
        self.app = create_app(config_name='test')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    @pytest.fixture(scope="module")
    def test_client(self):
        self.app = create_app(config_name='test')
        # 创建一个测试客户端
        testing_client = self.app.test_client()
        # 在模块级别创建所有表格
        with self.app.app_context():
            db.create_all()
        yield testing_client  # 返回客户端对象给测试函数
        # 在模块级别删除所有表格
        # with app.app_context():
        #     db.drop_all()

    @pytest.fixture(scope="module")
    def session(test_client):
        # 创建一个新的会话对象，并绑定到当前上下文中
        connection = db.engine.connect()
        transaction = connection.begin()
        options = dict(bind=connection, binds={})
        session = db.create_scoped_session(options=options)
        db.session = session

        yield session  # 返回会话对象给测试函数

        # 回滚事务并移除会话对象
        transaction.rollback()
        connection.close()
        session.remove()
