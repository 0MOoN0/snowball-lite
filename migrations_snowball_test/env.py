import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")


def get_engine():
    """
    获取 snowball 数据源的引擎，而不是默认引擎
    这样确保迁移只针对 snowball 数据库
    """
    try:
        # 获取 snowball 绑定的引擎
        migrate_ext = current_app.extensions["migrate"]
        if hasattr(migrate_ext.db, "engines") and "snowball" in migrate_ext.db.engines:
            # 使用 snowball 绑定的引擎
            return migrate_ext.db.engines["snowball"]
        elif hasattr(migrate_ext.db, "get_engine"):
            # Flask-SQLAlchemy < 3.0 的兼容性处理
            return migrate_ext.db.get_engine(bind="snowball")
        else:
            # Flask-SQLAlchemy >= 3.0 的处理
            return migrate_ext.db.get_engine(bind="snowball")
    except (TypeError, AttributeError, KeyError) as e:
        logger.error(f"无法获取 snowball 数据源引擎: {e}")
        # 如果获取 snowball 引擎失败，抛出异常而不是使用默认引擎
        raise RuntimeError("Flask-Migrate 配置错误：无法获取 snowball 数据源引擎")


def get_engine_url():
    """
    获取 snowball 数据源的连接URL
    """
    try:
        engine = get_engine()
        return engine.url.render_as_string(hide_password=False).replace("%", "%%")
    except AttributeError:
        return str(get_engine().url).replace("%", "%%")


# 设置 snowball 数据源的连接URL
config.set_main_option("sqlalchemy.url", get_engine_url())

# 获取 snowball 数据源的数据库对象
target_db = current_app.extensions["migrate"].db


def get_metadata():
    """
    获取元数据，确保只包含 snowball 数据源相关的表
    """
    if hasattr(target_db, "metadatas"):
        # Flask-SQLAlchemy >= 3.0
        # 如果有 snowball 绑定的元数据，使用它；否则使用默认元数据
        return target_db.metadatas.get("snowball", target_db.metadatas[None])
    else:
        # Flask-SQLAlchemy < 3.0
        return target_db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # 定义需要排除的表（APScheduler相关表）
    def include_object(object, name, type_, reflected, compare_to):
        """
        排除 APScheduler 相关的表，避免被误删
        """
        if type_ == "table":
            # 排除 APScheduler 相关表
            apscheduler_tables = {
                'apscheduler_jobs',
                'apscheduler_job_states', 
                'apscheduler_job_runs'
            }
            if name in apscheduler_tables:
                logger.info(f"排除 APScheduler 表: {name}")
                return False
        return True

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
        compare_type=True,  # 启用类型比较
        compare_server_default=True,  # 启用服务器默认值比较
        include_object=include_object,  # 添加表排除逻辑
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    # 定义需要排除的表（APScheduler相关表）
    def include_object(object, name, type_, reflected, compare_to):
        """
        排除 APScheduler 相关的表，避免被误删
        """
        if type_ == "table":
            # 排除 APScheduler 相关表
            apscheduler_tables = {
                'apscheduler_jobs',
                'apscheduler_job_states', 
                'apscheduler_job_runs'
            }
            if name in apscheduler_tables:
                logger.info(f"排除 APScheduler 表: {name}")
                return False
        return True

    conf_args = current_app.extensions["migrate"].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    # 添加额外的配置参数
    conf_args.update(
        {
            "compare_type": True,  # 启用类型比较
            "compare_server_default": True,  # 启用服务器默认值比较
            "include_object": include_object,  # 添加表排除逻辑
        }
    )

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=get_metadata(), **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
