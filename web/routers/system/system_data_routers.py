# -*- coding: UTF-8 -*-
"""
@File    ：system_data_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/10/5 21:40
"""
from flask import Blueprint, current_app
from flask_restful import Api, Resource, reqparse

from web.common.cache import cache
from web.common.cons import webcons
from web.common.utils import R
from web.databox import databox
import json

from web.weblogger import debug

system_bp = Blueprint("system", __name__, url_prefix="/system")
system_api = Api(system_bp)


def _redis_boundary_message(action: str) -> str:
    if current_app.config.get("_config_name") == "lite":
        return f"lite 模式下不支持{action}"
    return f"Redis 未启用，无法{action}"


# 获取菜单
class SystemDataRouter(Resource):
    def put(self):
        """
        @@@
        ```
        处理PUT请求，设置并保存token

        Args:
            无

        Returns:
            R.ok(): 操作成功返回的状态码和消息
        ```
        @@@
        """
        # 记录debug详细日志，打印相关参数
        debug("设置并保存token，开始")
        if not current_app.config.get("CACHE_AVAILABLE", False) or not cache.is_initialized():
            return R.fail(msg=_redis_boundary_message("系统 token 读写"))
        parse = reqparse.RequestParser()
        parse.add_argument('xq_a_token', required=True)
        parse.add_argument('u', required=True)
        parse.add_argument('serverchen_sendkey', required=True)
        system_data_post = parse.parse_args()
        debug("设置并保存token，参数 %s" % system_data_post)
        xq_token = {"xq_a_token": system_data_post['xq_a_token'], "u": system_data_post['u']}
        databox.set_token(key=webcons.DataBoxTokenKey.XQ_TOKEN, token=xq_token)
        cache.get_redis_client().set(webcons.RedisKey.XQ_TOKEN, json.dumps(xq_token))
        cache.get_redis_client().set(webcons.RedisKey.SERVERCHAN_SENDKEY, system_data_post["serverchen_sendkey"])
        debug("设置并保存token，结束")
        return R.ok()

    def get(self):
        """
        @@@
        ```
        处理GET请求，获取token

        Args:
            无

        Returns:
            R.ok(): 操作成功返回的状态码、消息和 token 数据
        ```
        @@@
        """
        # 记录debug详细日志
        debug("获取token，开始")
        if not current_app.config.get("CACHE_AVAILABLE", False) or not cache.is_initialized():
            return R.fail(msg=_redis_boundary_message("系统 token 查询"))
        setting = {}
        # 获取token
        token = databox.get_token(webcons.DataBoxTokenKey.XQ_TOKEN)
        serverchen_sendkey = cache.get_redis_client().get(webcons.RedisKey.SERVERCHAN_SENDKEY)
        setting.update(token)
        setting.update({"serverchen_sendkey": serverchen_sendkey})
        # 记录debug详细日志，打印参数
        debug("获取token，结束 %s" % setting)
        return R.ok(data=setting)


system_api.add_resource(SystemDataRouter, "/token")
