from time import time
import time as time_module
from sqlalchemy import event
import sqlalchemy.exc
import pymysql
import sqlparse  # 导入sqlparse库
import re  # 导入正则表达式模块

from web.decorator.auto_registry import ensure_models_registered
from web.models.base import db, migrate
from web.weblogger import debug, warning, error, info
from web.models import registry  # noqa: F401


def check_database_connection(engine, bind_name=None, max_retries=3, retry_delay=2):
    """
    检查数据库连接，并在连接失败时进行重试

    Args:
        engine: SQLAlchemy引擎实例
        bind_name: 数据库绑定名称（用于日志记录）
        max_retries: 最大重试次数
        retry_delay: 重试间隔（秒）

    Returns:
        bool: 数据库连接是否成功
    """
    db_name = f"[{bind_name}]" if bind_name else ""
    info(f"开始检查数据库连接 {db_name}...")

    for attempt in range(max_retries):
        try:
            # 使用 SQLAlchemy 2.0 兼容的方式执行查询
            with engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1")).fetchone()
                info(
                    f"数据库连接 {db_name} 检查成功 (尝试 {attempt + 1}/{max_retries})"
                )
                return True

        except (sqlalchemy.exc.OperationalError, pymysql.err.OperationalError) as e:
            error(f"数据库连接 {db_name} 失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                warning(f"将在{retry_delay}秒后重试数据库连接...")
                time_module.sleep(retry_delay)
            else:
                error(f"达到最大重试次数，数据库连接 {db_name} 仍然失败")
        except Exception as e:
            error(f"检查数据库连接 {db_name} 时发生未预期的错误: {e}", exc_info=True)
            if attempt < max_retries - 1:
                warning(f"将在{retry_delay}秒后重试数据库连接...")
                time_module.sleep(retry_delay)
            else:
                error(f"达到最大重试次数，数据库连接 {db_name} 检查失败")

    return False


def get_migration_directory(config_class_name):
    """
    根据配置类名称返回对应的迁移目录

    Args:
        config_class_name (str): 配置类名称

    Returns:
        str: 迁移目录路径
    """
    migration_mapping = {
        "DevConfig": "migrations_snowball_dev",
        "StgConfig": "migrations_snowball_stg",
        "ProdConfig": "migrations_snowball",
        "LocalDevTest": "migrations_snowball_dev",  # 本地开发测试使用开发环境迁移
        "TestingConfig": "migrations_snowball_test",
        "LiteConfig": "migrations_snowball_lite",
    }

    directory = migration_mapping.get(config_class_name, "migrations_snowball_dev")
    info(f"配置类 {config_class_name} 映射到迁移目录: {directory}")
    return directory


def _is_sqlite_file_database(engine):
    if engine.dialect.name != "sqlite":
        return False

    database = engine.url.database
    return bool(database and database != ":memory:")


def configure_sqlite_engine(engine):
    """为 SQLite engine 补齐最小运行时参数。"""
    if engine.dialect.name != "sqlite":
        return

    if getattr(engine, "_snowball_sqlite_configured", False):
        return

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=30000")

            if _is_sqlite_file_database(engine):
                cursor.execute("PRAGMA journal_mode=WAL")
        finally:
            cursor.close()

    engine._snowball_sqlite_configured = True


def ini_app(app):
    """初始化数据库模型并验证数据库连接"""
    app.logger.debug("### 加载models模块")

    # 初始化SQLAlchemy
    db.init_app(app)

    # 确保所有模型都已注册
    ensure_models_registered()

    # 根据配置类动态确定迁移目录
    config_class_name = app.config.get("_config_class_name", "DevConfig")
    info(f"配置类名称: {config_class_name}")
    migration_directory = get_migration_directory(config_class_name)

    # 初始化Flask-Migrate
    migrate.init_app(app, db, directory=migration_directory, compare_type=True)
    app.logger.info(
        f"Flask-Migrate初始化成功，配置类: {config_class_name}, 迁移目录: {migration_directory}"
    )

    # 初始化并检查数据库连接状态
    conn_success = True

    # 检查主数据库连接
    try:
        xalpha_engine = db.engine
        configure_sqlite_engine(xalpha_engine)
        if check_database_connection(xalpha_engine, "default"):
            # 根据配置决定是否注册引擎日志
            if app.config.get("ENABLE_ENGINE_LOG", True):
                try:
                    slow_query_threshold = app.config.get("SLOW_QUERY_THRESHOLD")
                    register_engine_log(xalpha_engine, slow_query_threshold)
                    info("成功注册默认数据库引擎日志")
                except Exception as e:
                    error(f"注册默认数据库引擎日志失败: {e}", exc_info=True)
            else:
                info("根据配置跳过默认数据库引擎日志注册")
        else:
            conn_success = False
            error("默认数据库连接失败，某些功能可能不可用")
    except Exception as e:
        conn_success = False
        error(f"获取默认数据库引擎失败: {e}", exc_info=True)

    # 检查snowball数据库连接
    try:
        # 检查是否配置了snowball绑定
        if "snowball" in app.config.get("SQLALCHEMY_BINDS", {}):
            snowball_engine = db.engines["snowball"]
            configure_sqlite_engine(snowball_engine)
            if check_database_connection(snowball_engine, "snowball"):
                # 根据配置决定是否注册引擎日志
                if app.config.get("ENABLE_ENGINE_LOG", True):
                    try:
                        slow_query_threshold = app.config.get("SLOW_QUERY_THRESHOLD")
                        register_engine_log(snowball_engine, slow_query_threshold)
                        info("成功注册snowball数据库引擎日志")
                    except Exception as e:
                        error(f"注册snowball数据库引擎日志失败: {e}", exc_info=True)
                else:
                    info("根据配置跳过snowball数据库引擎日志注册")
            else:
                conn_success = False
                error("snowball数据库连接失败，某些功能可能不可用")
    except Exception as e:
        conn_success = False
        error(f"获取snowball数据库引擎失败: {e}", exc_info=True)

    # 报告总体状态
    if conn_success:
        app.logger.info("所有数据库连接检查成功")
    else:
        app.logger.warning("一个或多个数据库连接检查失败，某些功能可能不可用")

    app.logger.debug("models模块加载完成 ###")

    return conn_success


def register_engine_log(engine, slow_query_threshold=None):
    """
    注册数据库引擎的日志监听器，用于监听SQL查询的执行情况。

    Args:
        engine (sqlalchemy.engine.Engine): 数据库引擎对象。
        slow_query_threshold (float, optional): 慢查询阈值（秒）。如果为None，则尝试从数据库获取或使用默认值。

    Returns:
        None

    """
    # 检查引擎是否有效
    if engine is None:
        error("无法注册引擎日志：引擎对象为空")
        return

    # 设置慢查询阈值
    if slow_query_threshold is not None:
        long_query_time = slow_query_threshold
        info(f"使用传入的慢查询阈值: {long_query_time}")
    else:
        # 设置默认的慢查询阈值
        long_query_time = 1.0  # 默认值

        if engine.dialect.name != "mysql":
            info(
                f"数据库方言 {engine.dialect.name} 不支持 MySQL 慢查询变量探测，使用默认阈值: {long_query_time}"
            )
        else:
            # 尝试获取long_query_time参数
            try:
                # 使用SQLAlchemy 2.0兼容的方式执行查询
                with engine.connect() as conn:
                    result = conn.execute(
                        sqlalchemy.text("show variables like 'long_query_time'")
                    ).fetchone()
                    if result:
                        long_query_time = float(result[1])
                        info(f"成功获取long_query_time参数: {long_query_time}")
            except Exception as e:
                warning(f"无法获取long_query_time参数，使用默认值 {long_query_time}: {e}")

    def format_sql_with_params(statement, parameters):
        """
        格式化SQL语句并尝试将参数插入到SQL中

        Args:
            statement: 原始SQL语句
            parameters: 查询参数，可能是字典、元组、列表等

        Returns:
            格式化后的SQL字符串
        """
        try:
            # 先使用sqlparse格式化SQL
            formatted_sql = sqlparse.format(
                statement, reindent=True, keyword_case="upper", indent_width=4
            )

            # 如果没有参数或参数为空，直接返回格式化的SQL
            if not parameters or (
                isinstance(parameters, (list, tuple)) and len(parameters) == 0
            ):
                return formatted_sql

            # 创建参数插入SQL的函数
            def try_insert_params():
                # 处理字典类型参数 (命名参数)
                if isinstance(parameters, dict):
                    result = formatted_sql
                    # 替换命名参数 如 :param 或 %(param)s
                    for key, value in parameters.items():
                        # 支持两种命名参数格式
                        patterns = [f":{key}\\b", f"%\\({key}\\)s"]
                        for pattern in patterns:
                            # 将参数值转换为SQL安全的字符串表示
                            if value is None:
                                sql_value = "NULL"
                            elif isinstance(value, (int, float)):
                                sql_value = str(value)
                            else:
                                # 字符串加引号，修复f-string中的转义问题
                                value_str = str(value)
                                escaped_value = value_str.replace("'", "''")
                                sql_value = f"'{escaped_value}'"

                            result = re.sub(pattern, sql_value, result)
                    return result

                # 处理元组、列表类型参数 (位置参数)
                elif isinstance(parameters, (list, tuple)):
                    result = formatted_sql
                    # 替换问号占位符
                    if "?" in result and len(parameters) > 0:
                        for param in parameters:
                            if param is None:
                                sql_value = "NULL"
                            elif isinstance(param, (int, float)):
                                sql_value = str(param)
                            else:
                                # 字符串加引号，修复f-string中的转义问题
                                param_str = str(param)
                                escaped_param = param_str.replace("'", "''")
                                sql_value = f"'{escaped_param}'"

                            # 只替换第一个问号
                            result = result.replace("?", sql_value, 1)
                        return result

                    # 当没有问号但有%s格式时，尝试替换%s
                    count = 0
                    parts = []
                    last_end = 0

                    # 查找所有的%s，但不包括%%s (转义的%)
                    for match in re.finditer(r"(?<!%)%s", result):
                        start, end = match.span()
                        if count < len(parameters):
                            parts.append(result[last_end:start])

                            param = parameters[count]
                            if param is None:
                                sql_value = "NULL"
                            elif isinstance(param, (int, float)):
                                sql_value = str(param)
                            else:
                                # 字符串加引号，修复f-string中的转义问题
                                param_str = str(param)
                                escaped_param = param_str.replace("'", "''")
                                sql_value = f"'{escaped_param}'"

                            parts.append(sql_value)
                            last_end = end
                            count += 1

                    if parts:
                        parts.append(result[last_end:])
                        return "".join(parts)

                # 如果无法处理，返回原始格式化SQL和单独的参数
                return None

            # 尝试插入参数
            sql_with_params = try_insert_params()
            if sql_with_params:
                return sql_with_params
            else:
                # 如果无法插入，至少返回格式化的SQL
                return formatted_sql

        except Exception as e:
            # 出错时记录日志，但仍然返回原始格式化SQL
            warning(f"格式化SQL参数时发生错误: {e}")
            return formatted_sql

    # 定义日志监听器
    info(f"正在为引擎 {engine} 注册SQL查询监听器")

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        try:
            conn.info.setdefault("query_start_time", []).append(time())

            # 使用新函数格式化SQL并插入参数
            formatted_sql = format_sql_with_params(statement, parameters)

            debug("执行SQL查询:")
            debug("\n" + formatted_sql)  # 打印格式化后且带参数的SQL语句

            # 仍然保留原始参数显示，便于调试
            if parameters:
                debug("原始参数: %s" % str(parameters))
        except Exception as e:
            error(f"在before_cursor_execute处理中发生错误: {e}", exc_info=True)

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        try:
            total = time() - conn.info["query_start_time"].pop(-1)
            debug("查询完成!")
            debug("执行时间: %.4f秒" % total)
            # 判断是否是慢查询
            if total > long_query_time:
                # 使用新函数格式化SQL并插入参数
                formatted_sql = format_sql_with_params(statement, parameters)

                warning(f"检测到慢查询! 执行时间: {total:.4f}秒")
                warning("慢查询SQL:\n" + formatted_sql)

                # 仍然保留原始参数显示，便于调试
                if parameters:
                    warning("原始参数: %s" % str(parameters))
        except Exception as e:
            error(f"在after_cursor_execute处理中发生错误: {e}", exc_info=True)

    info(f"SQL查询监听器注册成功，慢查询阈值设为: {long_query_time}秒")
