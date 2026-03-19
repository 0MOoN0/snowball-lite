# -*- coding: UTF-8 -*-
"""
@File    ：enum_version_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27 10:00
@Description: 枚举版本管理接口
"""

from flask import current_app
from flask_restx import Resource, Namespace, fields
from web.common.api_factory import get_api
from web.common.utils import R
from web.common.cache import cache
from web.common.enum.version_enum import VersionKeyEnum
from web.weblogger import debug, error
import json

# 创建Namespace
api_ns = Namespace("enum_versions", description="枚举版本管理接口")

# 获取全局API实例并注册namespace
api = get_api()
if api:
    api.add_namespace(api_ns, path="/api/enums")

# 定义响应模型
version_info_model = api_ns.model('VersionInfo', {
    'scope': fields.String(description='版本作用域'),
    'timestamp': fields.Float(description='版本时间戳'),
    'version': fields.String(description='版本号')
})

version_response_model = api_ns.model('VersionResponse', {
    'code': fields.Integer(description='响应代码'),
    'success': fields.Boolean(description='是否成功'),
    'message': fields.String(description='响应消息'),
    'data': fields.Raw(description='版本数据，键为版本键，值为版本信息对象')
})


def _redis_boundary_message(action: str) -> str:
    if current_app.config.get("_config_name") == "lite":
        return f"lite 模式下不支持{action}"
    return f"Redis 未启用，无法{action}"


@api_ns.route("/versions")
class EnumVersionRouters(Resource):
    @api_ns.doc("get_enum_versions")
    @api_ns.marshal_with(version_response_model)
    def get(self):
        """
        获取枚举版本信息
        
        从Redis中获取'version:enum'键的值，作为枚举版本信息返回。
        
        返回数据格式:
        - 成功响应格式：{"code": 20000, "data": {"global": 1756120775}, "message": "获取枚举版本成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}
        
        数据格式说明:
        - 返回数据为字典格式，包含各个作用域的版本信息
        - 版本信息对象包含时间戳（timestamp）和版本号（version）等详情
        
        关键注意事项:
        - 需要Redis连接正常，否则返回失败响应
        - 版本数据格式为JSON，解析失败时返回错误响应
        - 专门返回枚举版本数据，不包含其他类型的版本信息
        
        请求示例:
        GET /api/enums/versions
        
        返回示例:
        成功响应:
        {
            "code": 20000,
            "success": true,
            "message": "获取枚举版本成功",
            "data": {
                "global": 1756120775
            }
        }
        
        失败响应:
        {
            "code": 20500,
            "success": false,
            "message": "Redis连接失败",
            "data": false
        }
        """
        try:
            debug("开始获取枚举版本信息")
            if not current_app.config.get("CACHE_AVAILABLE", False) or not cache.is_initialized():
                return R.fail(msg=_redis_boundary_message("枚举版本查询"))
            
            # 获取Redis客户端
            redis_client = cache.get_redis_client()
            if not redis_client:
                error("Redis客户端获取失败", exc_info=True)
                return R.fail(msg="Redis连接失败")
            
            # 获取枚举版本数据
            enum_version_key = VersionKeyEnum.ENUM.value
            value = redis_client.get(enum_version_key)
            debug(f"获取枚举版本键: {enum_version_key}")
            
            if not value:
                debug(f"枚举版本键 {enum_version_key} 的值为空")
                return R.ok(data={}, msg="获取枚举版本成功")
            
            try:
                # 解析JSON数据
                value_str = value.decode('utf-8') if isinstance(value, bytes) else value
                version_data = json.loads(value_str)
                debug(f"成功解析枚举版本数据: {version_data}")
                return R.ok(data=version_data, msg="获取枚举版本成功")
                
            except json.JSONDecodeError as e:
                error(f"解析枚举版本JSON数据失败: {e}", exc_info=True)
                return R.fail(msg="枚举版本数据格式错误")
            
        except Exception as e:
            error(f"获取枚举版本信息失败: {e}", exc_info=True)
            return R.fail(msg="获取枚举版本信息失败")
