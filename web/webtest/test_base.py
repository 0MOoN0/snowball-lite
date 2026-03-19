# 定义一个应用的fixture，使用TestConfig作为配置，并设置scope为session
import pytest


# 定义一个测试基类，继承自object，并使用client和session作为参数
@pytest.mark.usefixtures('app', "client", "session")
class TestBase(object):
    """
    基础测试类
    
    使用场景：
    - 适用于一般的API接口测试
    - 需要Flask应用上下文、测试客户端和数据库会话的测试
    - 每个测试函数都会创建和清理数据库表
    
    包含的fixtures：
    - app: Flask应用实例，scope为session
    - client: Flask测试客户端，scope为session
    - session: 数据库会话，scope为function，每个测试函数后会清理
    
    注意事项：
    - 测试数据在每个测试函数后会被清理
    - 适合需要真实数据库操作的测试场景
    """
    pass


@pytest.mark.usefixtures('app', 'client', 'rollback_session')
class TestBaseWithRollback(object):
    """
    带事务回滚的测试基类
    
    使用场景：
    - 需要数据库事务隔离的测试
    - 测试完成后自动回滚所有数据库操作
    - 适用于复杂的数据库操作测试，确保测试间数据完全隔离
    - 特别适合测试绑定到'snowball'数据库的模型
    
    包含的fixtures：
    - app: Flask应用实例，scope为session
    - client: Flask测试客户端，scope为session  
    - rollback_session: 带事务回滚的数据库会话，scope为function
    
    优势：
    - 每个测试在独立事务中运行
    - 测试结束后自动回滚，不影响其他测试
    - 提供更好的测试隔离性
    
    注意事项：
    - 主要用于测试绑定到'snowball'数据库的模型
    - 事务会在测试结束时自动回滚
    """
    pass


@pytest.mark.usefixtures('lite_webtest_app', 'lite_webtest_client', 'lite_rollback_session')
class TestBaseLiteWithRollback(object):
    """
    stage3 SQLite 集成测试基类

    使用场景：
    - 第三阶段专项 SQLite 集成测试
    - 需要复用 web/webtest 现有测试组织方式，但不依赖 MySQL server
    - 需要和 lite 专用 bootstrap 及临时缓存目录配套运行

    包含的 fixtures：
    - lite_webtest_app: stage3 专用 lite 应用实例，scope 为 session
    - lite_webtest_client: stage3 专用测试客户端，scope 为 session
    - lite_rollback_session: 绑定 SQLite 连接的事务回滚会话，scope 为 function

    注意事项：
    - 仅面向 stage3 选定范围，不替换原有 MySQL webtest 基类
    - SQLite 临时库和缓存目录都由 fixture 统一提供
    """
    pass


@pytest.mark.usefixtures('test_db_app', 'test_db_session')
class TestBaseForAssetModels(object):
    """
    专用于Asset和AssetCode模型测试的基类
    
    使用场景：
    - 专门用于测试Asset和AssetCode等绑定到'snowball'数据库的模型
    - 需要完整数据库环境和表结构的测试
    - 适合复杂的模型关系测试和数据完整性测试
    
    包含的fixtures：
    - test_db_app: 测试数据库应用实例，依赖setup_test_database
    - test_db_session: 专用于Asset模型的数据库会话，带事务隔离
    
    特点：
    - 确保测试数据库存在并创建了所有表结构
    - 每个测试使用独立事务，测试结束后回滚
    - 专门针对'snowball'数据库绑定的模型设计
    
    注意事项：
    - 需要正确配置测试数据库环境变量
    - 测试结束后不删除表结构，只回滚事务
    - 如果'snowball'绑定不存在会抛出ValueError
    """
    pass


@pytest.mark.usefixtures('setup_test_database')
class TestBaseForDatabaseSetup(object):
    """
    数据库设置测试基类
    
    使用场景：
    - 测试数据库连接和配置
    - 验证数据库创建和初始化逻辑
    - 测试数据库迁移相关功能
    - 不需要应用上下文的纯数据库测试
    
    包含的fixtures：
    - setup_test_database: 确保测试数据库存在，但不创建表结构
    
    特点：
    - 只负责数据库的创建，不涉及表结构
    - 适合测试数据库连接和基础配置
    - 轻量级的数据库测试环境
    
    注意事项：
    - 不包含Flask应用上下文
    - 不自动创建数据库表
    - 需要手动管理数据库连接
    """
    pass


@pytest.mark.usefixtures('app')
class TestBaseAppOnly(object):
    """
    仅包含应用上下文的测试基类
    
    使用场景：
    - 测试不需要数据库操作的功能
    - 测试应用配置和初始化
    - 测试工具函数和辅助方法
    - 测试模板渲染和静态资源
    
    包含的fixtures：
    - app: Flask应用实例，scope为session
    
    特点：
    - 轻量级测试环境
    - 只提供Flask应用上下文
    - 不涉及数据库操作
    
    适用测试：
    - 配置测试
    - 工具函数测试  
    - 模板渲染测试
    - 路由注册测试
    
    注意事项：
    - 不包含数据库会话
    - 不包含测试客户端
    - 适合单元测试而非集成测试
    """
    pass


@pytest.mark.usefixtures('app', 'client')
class TestBaseApiOnly(object):
    """
    API接口测试专用基类
    
    使用场景：
    - 专门用于API接口的HTTP请求测试
    - 测试路由、中间件、请求处理等
    - 不涉及数据库操作的API测试
    - Mock数据库操作的API测试
    
    包含的fixtures：
    - app: Flask应用实例，scope为session
    - client: Flask测试客户端，scope为session
    
    特点：
    - 提供HTTP客户端进行请求测试
    - 不包含数据库会话，避免数据库依赖
    - 适合使用Mock的API测试
    
    适用测试：
    - HTTP状态码测试
    - 请求参数验证测试
    - 响应格式测试
    - 路由匹配测试
    - 中间件功能测试
    
    注意事项：
    - 需要Mock数据库操作
    - 专注于API层面的测试
    - 不进行真实的数据库操作
    """
    pass
