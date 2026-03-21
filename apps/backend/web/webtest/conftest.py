from contextlib import contextmanager
import os
from pathlib import Path
from urllib.parse import quote_plus

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from web import create_app
from web.lite_bootstrap import bootstrap_lite_database
from web.models import db
from web.models.setting.system_settings import Setting
from web.webtest.lite_runtime_guard import ensure_test_lite_db_path_isolated
from web.webtest.mysql_test_guard import (
    MYSQL_INTEGRATION_MARK,
    should_run_mysql_integration,
    uses_mysql_test_fixtures,
    validate_mysql_test_database_names,
)

"""
pytest配置文件，定义基础的fixtures
"""


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    mysql_items = []
    for item in items:
        if uses_mysql_test_fixtures(item.fixturenames):
            item.add_marker(getattr(pytest.mark, MYSQL_INTEGRATION_MARK))
            mysql_items.append(item)

    if not mysql_items or should_run_mysql_integration(config.option.markexpr):
        return

    remaining_items = [item for item in items if item not in mysql_items]
    config.hook.pytest_deselected(items=mysql_items)
    items[:] = remaining_items


@pytest.fixture(scope="session", params=['test'])
def app(request):
    # 日志输出参数
    if request.param == "test":
        validate_mysql_test_database_names(
            os.environ.get("TEST_DB_TESTDB", "snowball_test"),
            os.environ.get("TEST_DB_DATABASE", "snowball_data_test"),
        )
    app = create_app(config_name=request.param)
    app.logger.debug('request.param : ' + request.param)
    with app.app_context():
        yield app


# 定义一个客户端的fixture，使用app作为参数，并设置scope为session，返回一个test_client
@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


# 定义一个数据库会话的fixture，使用app作为参数，并设置scope为function
@pytest.fixture(scope="function")
def session(app):
    yield db.session
    # 在每个测试函数之后删除所有表格并移除会话对象
    # db.drop_all()
    db.session.remove()


@pytest.fixture(scope='function')
def rollback_session(app):   
    # 连接数据库并开启事务
    connection = db.engines['snowball'].connect()  # 使用 'snowball' 数据源
    transaction = connection.begin()

    # 使用 scoped_session 代替 create_scoped_session
    # 指定 query_cls 为 db.Query，使其支持 paginate 方法
    session_factory = sessionmaker(bind=connection, query_cls=db.Query)
    session = scoped_session(session_factory)
    
    # 为session添加remove方法兼容Flask-SQLAlchemy 3.0.3
    original_remove = session.remove
    
    def enhanced_remove():
        # 先调用原始的scoped_session.remove方法
        original_remove()
        # 然后确保连接正确关闭
        if not connection.closed:
            connection.close()
    
    session.remove = enhanced_remove

    db.session = session

    yield db.session

    # 清理资源：先移除session，再回滚事务，最后关闭连接
    try:
        session.remove()
    except Exception:
        pass  # 忽略session移除时的异常
    
    try:
        if transaction.is_active:
            transaction.rollback()
    except Exception:
        pass  # 忽略事务回滚时的异常
    
    try:
        if not connection.closed:
            connection.close()
    except Exception:
        pass  # 忽略连接关闭时的异常


@contextmanager
def _temporary_lite_runtime_env(root: Path):
    db_path = ensure_test_lite_db_path_isolated(
        root / "pytest-snowball-lite-stage3.db"
    )
    cache_dir = root / "pytest-lite_xalpha_cache"
    old_env = {
        "LITE_DB_PATH": os.environ.get("LITE_DB_PATH"),
        "LITE_XALPHA_CACHE_DIR": os.environ.get("LITE_XALPHA_CACHE_DIR"),
        "LITE_XALPHA_CACHE_BACKEND": os.environ.get("LITE_XALPHA_CACHE_BACKEND"),
    }

    os.environ["LITE_DB_PATH"] = str(db_path)
    os.environ["LITE_XALPHA_CACHE_DIR"] = str(cache_dir)
    os.environ["LITE_XALPHA_CACHE_BACKEND"] = "csv"

    try:
        yield {
            "root": root,
            "db_path": db_path,
            "cache_dir": cache_dir,
        }
    finally:
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@pytest.fixture(scope="session")
def lite_webtest_runtime(tmp_path_factory):
    root = Path(tmp_path_factory.mktemp("pytest-lite-webtest-stage3"))
    with _temporary_lite_runtime_env(root) as runtime:
        yield runtime


@pytest.fixture(scope="session")
def lite_webtest_app(lite_webtest_runtime):
    app = create_app(config_name="lite")

    with app.app_context():
        bootstrap_lite_database(app)

    yield app

    with app.app_context():
        db.session.remove()

    for engine in db.engines.values():
        engine.dispose()


@pytest.fixture(scope="session")
def lite_webtest_client(lite_webtest_app):
    return lite_webtest_app.test_client()


@pytest.fixture(scope="function")
def lite_rollback_session(lite_webtest_app):
    engine = db.engines.get("snowball", db.engine)
    connection = engine.connect()
    transaction = connection.begin()

    session_factory = sessionmaker(bind=connection, query_cls=db.Query)
    session = scoped_session(session_factory)
    original_session = db.session

    original_remove = session.remove

    def enhanced_remove():
        original_remove()
        if not connection.closed:
            connection.close()

    session.remove = enhanced_remove
    db.session = session

    yield db.session

    try:
        session.remove()
    except Exception:
        pass

    try:
        if transaction.is_active:
            transaction.rollback()
    except Exception:
        pass

    try:
        if not connection.closed:
            connection.close()
    except Exception:
        pass

    db.session = original_session


@pytest.fixture(scope="session")
def setup_test_database():
    """
    创建测试数据库（如果不存在），但不创建表结构
    测试结束后不删除数据库，只清空表数据
    """
    # 从环境变量或使用默认值获取数据库连接信息
    dialect = os.environ.get("DB_DIALECT", "mysql")
    driver = os.environ.get("DB_DRIVER", "pymysql")
    username = os.environ.get("TEST_DB_USERNAME", "root")
    password = quote_plus(os.environ.get("TEST_DB_PASSWORD", "root"))
    host = os.environ.get("TEST_DB_HOST", "localhost")
    port = os.environ.get("TEST_DB_PORT", "3306")
    
    # 获取测试数据库名称
    test_db_name = os.environ.get("TEST_DB_TESTDB", "snowball_test")
    data_db_name = os.environ.get("TEST_DB_DATABASE", "snowball_data_test")
    # profiler_db_name = os.environ.get("TEST_DB_PROFILER", "snowball_profiler_test")  # 移除profiler数据库

    validate_mysql_test_database_names(test_db_name, data_db_name)
    
    # 连接到MySQL服务器（不指定数据库）
    root_engine = create_engine(
        f"{dialect}+{driver}://{username}:{password}@{host}:{port}", 
        echo=False,
        isolation_level="AUTOCOMMIT"  # 自动提交模式，允许执行DDL语句
    )
    
    print("检查测试数据库是否存在...")
    
    # 创建数据库
    conn = root_engine.connect()
    databases = [test_db_name, data_db_name]  # 移除profiler_db_name
    
    # 创建数据库（如果不存在）
    for db_name in databases:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        print(f"确保数据库存在: {db_name}")
    
    conn.close()
    root_engine.dispose()
    
    yield


@pytest.fixture(scope="session")
def test_db_app(setup_test_database):
    """
    创建一个使用测试配置的应用实例，用于数据库测试
    依赖于setup_test_database，确保应用创建前数据库已存在
    
    创建表结构（如果不存在）
    测试结束后不删除表结构，只移除会话
    """
    app = create_app(config_name="test")
    
    with app.app_context():
        # 创建所有表（如果不存在）
        try:
            app.logger.info("开始创建数据库表...")
            db.create_all()  # 这会创建所有数据库的表，包括绑定的数据库
            app.logger.info("所有数据库表创建完成")
        except Exception as e:
            app.logger.error(f"创建数据表时出错: {str(e)}")
            raise
        
        yield app
        
        # 测试结束时不删除表结构，只移除会话
        db.session.remove()


@pytest.fixture(scope="function")
def test_db_session(test_db_app):
    """
    为每个测试函数提供一个隔离的会话，专用于测试Asset和AssetCode模型。
    每个测试使用独立的事务，测试结束后回滚事务，确保测试间数据隔离。
    
    注意：此fixture主要用于测试绑定到'snowball'数据库的模型。
    """
    from sqlalchemy.orm import Session
    
    with test_db_app.app_context():
        # 获取snowball引擎
        if 'snowball' not in db.engines:
            raise ValueError("'snowball'绑定不存在，无法测试Asset和AssetCode模型")
        
        engine = db.engines['snowball']
        
        # 创建连接和事务
        connection = engine.connect()
        transaction = connection.begin()
        
        # 创建会话
        session = Session(bind=connection)
        
        # 为session添加remove方法，兼容Flask-SQLAlchemy 3.0.3
        def remove():
            session.close()
        
        session.remove = remove
        
        # 替换Flask-SQLAlchemy会话
        original_session = db.session
        db.session = session
        
        try:
            yield session
        finally:
            # 清理
            session.close()
            transaction.rollback()
            connection.close()
            
            # 恢复原始会话
            db.session = original_session


@pytest.fixture(scope="function")
def setup_system_setting():
    """
    通用的系统设置配置fixture
    
    提供一个通用的函数来设置系统配置到数据库，可以被任何需要操作Setting模型的测试使用
    这个fixture不依赖于特定的业务逻辑，可以用于各种测试场景
    
    Returns:
        function: 用于设置系统配置的函数
    """
    def _setup_setting(session, config_key: str, config_value: str, 
                      group: str = "test", description: str = None, 
                      setting_type: str = "string"):
        """
        设置系统配置到数据库
        
        Args:
            session: 数据库会话
            config_key: 配置键
            config_value: 配置值
            group: 配置分组，默认为"test"
            description: 配置描述
            setting_type: 配置类型，默认为"string"
        """
        # 查找现有配置
        setting = session.query(Setting).filter_by(key=config_key).first()
        if setting:
            setting.value = config_value
            if group:
                setting.group = group
            if description:
                setting.description = description
            if setting_type:
                setting.setting_type = setting_type
        else:
            # 创建新配置
            setting = Setting(
                key=config_key,
                value=config_value,
                group=group or "test",
                description=description or f"测试配置 - {config_key}",
                setting_type=setting_type or "string"
            )
            session.add(setting)
        session.flush()
    
    return _setup_setting


@pytest.fixture(scope="function")
def batch_setup_system_settings(setup_system_setting):
    """
    批量设置系统配置的fixture
    
    提供一个通用的函数来批量设置系统配置到数据库
    
    Args:
        setup_system_setting: 设置单个配置的函数
        
    Returns:
        function: 用于批量设置配置的函数
    """
    def _batch_setup_settings(session, settings_dict: dict, 
                             default_group: str = "test", 
                             default_description_prefix: str = "测试配置"):
        """
        批量设置系统配置到数据库
        
        Args:
            session: 数据库会话
            settings_dict: 配置字典，格式为 {key: value} 或 {key: {"value": value, "group": group, ...}}
            default_group: 默认配置分组
            default_description_prefix: 默认描述前缀
        """
        for config_key, config_data in settings_dict.items():
            if isinstance(config_data, dict) and "value" in config_data:
                # 详细配置格式
                setup_system_setting(
                    session,
                    config_key,
                    config_data["value"],
                    config_data.get("group", default_group),
                    config_data.get("description", f"{default_description_prefix} - {config_key}"),
                    config_data.get("setting_type", "string")
                )
            else:
                # 简单配置格式
                setup_system_setting(
                    session,
                    config_key,
                    str(config_data),
                    default_group,
                    f"{default_description_prefix} - {config_key}"
                )
    
    return _batch_setup_settings
