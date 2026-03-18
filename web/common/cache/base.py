# -*- coding: UTF-8 -*-
"""
@File    ：base.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/10/8 19:46
"""

from __future__ import annotations


class Cache:
    def __init__(self):
        self.redis_client = None

    @staticmethod
    def _load_redis_module():
        import redis

        return redis

    def reset(self):
        if self.redis_client is not None:
            try:
                self.redis_client.close()
            except Exception:
                pass
        self.redis_client = None

    def init_app(self, app):
        self.reset()
        # 获取 Redis 配置
        redis_config = app.config.get("REDIS_CLIENT")
        if not redis_config:
            raise RuntimeError("REDIS_CLIENT config is missing")
        redis_module = self._load_redis_module()
        # 创建 Redis 客户端，添加密码参数
        self.redis_client = redis_module.Redis(
            host=redis_config["REDIS_HOST"],
            port=redis_config["REDIS_PORT"],
            db=redis_config["REDIS_DB"],
            password=redis_config.get("REDIS_PASSWORD"),  # 获取密码，如果没有则为 None
            decode_responses=True,
        )

    def is_initialized(self) -> bool:
        return self.redis_client is not None

    def get_redis_client(self):
        if not self.redis_client:
            raise RuntimeError("cache module is not initialized")
        return self.redis_client


cache = Cache()
