from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger, Integer
from sqlalchemy.types import TypeDecorator


class SQLiteCompatibleBigInteger(TypeDecorator):
    """在 SQLite 下退化为 INTEGER，保留主键自增语义。"""

    impl = BigInteger
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "sqlite":
            return dialect.type_descriptor(Integer())
        return dialect.type_descriptor(BigInteger())

db = SQLAlchemy()
migrate = Migrate()

# 让现有模型继续使用 db.BigInteger 写法，同时在 SQLite 下拿到 INTEGER PRIMARY KEY。
db.BigInteger = SQLiteCompatibleBigInteger
