# -*- coding: UTF-8 -*-
"""
@File    ：system_settings_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/2/16 15:30
"""

from flask_restx import Resource, Namespace, reqparse
from marshmallow import ValidationError

from typing import List, Dict, Any
from web.common.api_factory import get_api
from web.common.utils import R
from web.models import db
from web.models.setting.system_settings import (
    Setting,
    SettingSchema, SettingUpdateSchema,
)
from web.weblogger import debug, error
# 修改导入，因为 create_system_settings_models 现在返回更具体的模型
from .system_settings_schemas import create_system_settings_models
from ..common.response_schemas import pagination_response_model
from web.services.system.system_settings_batch_service import SystemSettingsBatchService

# 创建Namespace
api_ns = Namespace("system_settings", description="系统设置管理接口")

# 获取全局API实例并注册namespace
api = get_api()
if api:
    api.add_namespace(api_ns, path="/system/settings")

# 创建API模型
# 现在 create_system_settings_models 返回一个包含所有相关模型的字典
all_models = create_system_settings_models(api_ns)
setting_model = all_models["setting_model"]
setting_create_model = all_models["setting_create_model"]
setting_update_model = all_models["setting_update_model"]
# 使用响应模型
single_setting_response_model = all_models["single_setting_response_model"]
# 批量更新相关模型
setting_batch_update_model = all_models["setting_batch_update_model"]
batch_update_response_model = all_models["batch_update_response_model"]

# 查询参数解析器
query_parser = reqparse.RequestParser()
query_parser.add_argument("key", type=str, help="设置项唯一标识键")
query_parser.add_argument("group", type=str, help="设置分组")
query_parser.add_argument("settingType", type=str, help="设置类型")
query_parser.add_argument("page", type=int, default=1, help="页码")
query_parser.add_argument("size", type=int, default=20, help="每页大小")


@api_ns.route("/")
class SystemSettingsRouters(Resource):
    """系统设置路由类"""

    @api_ns.doc("get_system_settings")
    @api_ns.expect(query_parser)
    @api.marshal_with(pagination_response_model)
    def get(self):
        """
        系统设置查询接口

        根据key、group和settingType查询系统设置信息，支持单个查询和批量查询。

        请求参数:
        - key (string, optional): 设置项唯一标识键，支持模糊匹配
        - group (string, optional): 设置分组，支持模糊匹配
        - settingType (string, optional): 设置类型，支持模糊匹配
        - page (int, optional): 页码，默认为1
        - size (int, optional): 每页大小，默认为20，最大100

        使用示例:
        - 查询所有设置：GET /system/settings
        - 根据key模糊查询：GET /system/settings?key=email （匹配包含'email'的所有key）
        - 根据group模糊查询：GET /system/settings?group=mail （匹配包含'mail'的所有group）
        - 根据settingType模糊查询：GET /system/settings?settingType=string （匹配包含'string'的所有settingType）
        - 分页查询：GET /system/settings?page=1&size=10
        - 组合查询：GET /system/settings?group=email&settingType=string&page=1&size=5
        """
        debug("查询系统设置，开始")

        # 解析查询参数
        args = query_parser.parse_args()
        debug(f"查询系统设置，参数：{args}")

        try:
            # 构建查询条件
            query = Setting.query

            if args["key"]:
                query = query.filter(Setting.key.like('%' + args['key'] + '%'))

            if args["group"]:
                query = query.filter(Setting.group.like('%' + args['group'] + '%'))

            if args["settingType"]:
                query = query.filter(Setting.setting_type.like('%' + args['settingType'] + '%'))

            # 分页处理
            page = max(1, args["page"])
            size = min(100, max(1, args["size"]))  # 限制最大页面大小为100

            # 执行分页查询
            pagination = query.paginate(page=page, per_page=size, error_out=False)

            # 序列化结果
            schema = SettingSchema(many=True)
            items = schema.dump(pagination.items)

            result = {
                "items": items,
                "total": pagination.total,
                "page": page,
                "size": size,
            }

            debug(f"查询系统设置，结果数量：{len(items)}")
            return R.ok(data=result)

        except Exception as e:
            error(f"查询系统设置失败：{str(e)}")
            return R.fail(msg=f"查询失败：{str(e)}")

    @api_ns.doc("create_system_setting")
    @api_ns.expect(setting_create_model)
    @api_ns.marshal_with(single_setting_response_model)
    def post(self):
        """
        系统设置新增接口

        创建新的系统设置项。

        请求体参数:
        - key (string, required): 设置项唯一标识键，不能与现有设置重复
        - value (string, required): 设置项的值
        - group (string, required): 设置分组，用于分类管理
        - description (string, optional): 设置项的描述信息
        - data_type (string, optional): 数据类型，如 string、number、boolean 等
        - is_public (boolean, optional): 是否为公开设置，默认为 false
        - sort_order (integer, optional): 排序顺序，默认为 0

        返回数据:
        - 成功时返回创建的设置项完整信息
        - 失败时返回错误信息

        使用示例:
        POST /system/settings
        {
            "key": "email_smtp_host",
            "value": "smtp.example.com",
            "group": "email",
            "description": "邮件服务器地址",
            "dataType": "string",
            "isPublic": false
        }
        """
        debug("新增系统设置，开始")
    
        try:
            # 使用 api.payload 获取已校验的数据
            json_data = api_ns.payload
            debug(f"新增系统设置，参数：{json_data}")
    
            # 使用Marshmallow Schema进行反序列化
            schema = SettingSchema()
            try:
                # 这里会自动处理data_key映射
                new_setting = schema.load(json_data)
            except ValidationError as ve:
                return R.fail(msg=f"数据验证失败：{ve.messages}")
    
            # 检查key是否已存在
            existing_setting = Setting.query.filter_by(key=new_setting.key).first()
            if existing_setting:
                return R.fail(msg=f"设置项key '{new_setting.key}' 已存在")
    
            # 保存到数据库
            db.session.add(new_setting)
            db.session.commit()
    
            # 返回创建的数据
            result = schema.dump(new_setting)
            debug(f"新增系统设置成功，ID：{new_setting.id}")
            return R.ok(data=result, msg="设置项创建成功")
    
        except Exception as e:
            db.session.rollback()
            error(f"新增系统设置失败：{str(e)}")
            return R.fail(msg=f"创建失败：{str(e)}")

    @api_ns.doc("update_system_setting")
    @api_ns.expect(setting_update_model)
    @api_ns.marshal_with(single_setting_response_model)
    def put(self):
        """
        系统设置更新接口

        根据key更新现有的系统设置项，支持更新配置名称、配置值、配置类型、所属分组、配置描述、默认值等字段。

        请求体参数:
        - key (string, required): 设置项唯一标识键，必须是已存在的设置项
        - value (string, required): 设置项的新值
        - settingType (string, optional): 设置类型，可选值：string/int/float/bool/json/password
        - group (string, optional): 设置分组，如：general/email/security/notification等
        - description (string, optional): 设置项的描述信息
        - defaultValue (string, optional): 设置项的默认值

        返回数据:
        - 成功时返回更新后的设置项完整信息
        - 失败时返回错误信息

        注意事项:
        - 只能更新已存在的设置项，不存在的key会返回错误
        - key字段用于定位要更新的设置项，不能修改key本身
        - 当settingType为json时，会对value进行JSON格式校验
        - 如果不提供可选字段，则保持原值不变
        - 所有字段都支持通过此接口进行更新

        使用示例:
        PUT /system/settings
        {
            "key": "email_smtp_host",
            "value": "smtp.newserver.com",
            "settingType": "string",
            "group": "email",
            "description": "更新后的邮件服务器地址",
            "defaultValue": "smtp.default.com"
        }
        
        JSON类型配置示例:
        PUT /system/settings
        {
            "key": "notification_config",
            "value": "{\"email\": true, \"sms\": false}",
            "settingType": "json",
            "description": "通知配置"
        }
        """
        debug("更新系统设置，开始")

        try:
            # 使用 api.payload 获取已校验的数据
            json_data = api_ns.payload
            debug(f"更新系统设置，参数：{json_data}")

            # 查找要更新的设置项
            setting = Setting.query.filter_by(key=json_data["key"]).first()
            if not setting:
                return R.fail(msg=f"设置项key '{json_data['key']}' 不存在")

            # 使用SettingUpdateSchema进行数据校验
            update_schema = SettingUpdateSchema()
            
            # 为JSON校验设置当前设置类型
            update_schema._current_setting_type = setting.setting_type
            
            try:
                validated_data = update_schema.load(json_data)
            except ValidationError as ve:
                return R.fail(msg=f"数据验证失败：{ve.messages}")

            # 更新字段
            setting.value = validated_data["value"]
            
            # 可选字段更新
            if "setting_type" in validated_data and validated_data["setting_type"] is not None:
                setting.setting_type = validated_data["setting_type"]
            if "group" in validated_data and validated_data["group"] is not None:
                setting.group = validated_data["group"]
            if "description" in validated_data and validated_data["description"] is not None:
                setting.description = validated_data["description"]
            if "default_value" in validated_data and validated_data["default_value"] is not None:
                setting.default_value = validated_data["default_value"]

            # 保存更改
            db.session.commit()

            # 返回更新后的数据
            schema = SettingSchema()
            result = schema.dump(setting)
            debug(f"更新系统设置成功，key：{setting.key}")
            return R.ok(data=result, msg="设置项更新成功")

        except Exception as e:
            db.session.rollback()
            error(f"更新系统设置失败：{str(e)}")
            return R.fail(msg=f"更新失败：{str(e)}")




@api_ns.route("/<int:setting_id>")
class SystemSettingByIdRouters(Resource):
    """根据ID操作系统设置的路由类"""

    @api_ns.doc("delete_system_setting_by_id")
    def delete(self, setting_id):
        """
        根据ID删除系统设置接口

        根据设置项的ID删除指定的系统设置。

        路径参数:
        - setting_id (int, required): 要删除的设置项ID

        返回数据:
        - 成功时返回删除确认信息
        - 失败时返回错误信息

        注意事项:
        - 删除操作不可逆，请谨慎使用
        - 删除不存在的ID会返回404错误
        - 建议在删除前先通过查询接口确认要删除的设置项

        使用示例:
        DELETE /system/settings/123
        """
        debug(f"删除系统设置，ID：{setting_id}")

        try:
            # 查找要删除的设置项
            setting = Setting.query.get(setting_id)
            if not setting:
                return R.fail(msg=f"设置项ID '{setting_id}' 不存在", code=404)

            # 记录要删除的设置项信息（用于日志）
            setting_key = setting.key
            setting_group = setting.group

            # 执行删除
            db.session.delete(setting)
            db.session.commit()

            debug(f"删除系统设置成功，ID：{setting_id}，key：{setting_key}，group：{setting_group}")
            return R.ok(msg=f"设置项删除成功（ID: {setting_id}, key: {setting_key}）")

        except Exception as e:
            db.session.rollback()
            error(f"删除系统设置失败，ID：{setting_id}，错误：{str(e)}")
            return R.fail(msg=f"删除失败：{str(e)}")


@api_ns.route("/batch")
class SystemSettingsBatchRouters(Resource):
    """系统设置批量操作路由类"""

    @api_ns.doc("batch_update_system_settings")
    @api_ns.expect(setting_batch_update_model)
    @api_ns.marshal_with(batch_update_response_model)
    def put(self):
        """
        系统设置批量更新接口

        支持一次性更新多个系统设置项，采用部分成功策略，即使部分设置项更新失败，
        其他成功的设置项仍会被保存。适用于批量配置更新、系统初始化等场景。

        核心特性:
        - 部分成功策略：单个设置项失败不影响其他设置项的更新
        - 详细错误报告：返回每个失败项的具体错误信息
        - 高性能：使用批量查询优化数据库访问
        - 类型安全：完整的类型提示和数据验证
        - 可扩展性：支持未来添加更多批量操作功能

        请求体参数:
        - settings (array, required): 要批量更新的设置项列表，最多50项
          - key (string, required): 设置项唯一标识键，必须是已存在的设置项
          - value (string, optional): 设置项的新值
          - settingType (string, optional): 设置类型，可选值：string/int/float/bool/json/password
          - group (string, optional): 设置分组，如：general/email/security/notification等
          - description (string, optional): 设置项的描述信息
          - defaultValue (string, optional): 设置项的默认值

        返回数据:
        - success_count (int): 成功更新的设置项数量
        - failure_count (int): 更新失败的设置项数量
        - successful_keys (array): 成功更新的设置项key列表
        - failures (array): 失败详情列表，包含key和错误信息

        安全特性:
        - 输入验证：严格的数据格式和类型检查
        - 存在性检查：只能更新已存在的设置项
        - JSON格式验证：当settingType为json时自动验证JSON格式
        - 事务管理：确保数据一致性
        - 错误隔离：单个设置项错误不影响其他设置项
        - 数量限制：单次最多更新50个设置项，防止系统过载

        性能优化:
        - 批量查询：一次性获取所有需要更新的设置项
        - 减少数据库往返：最小化数据库交互次数
        - 内存优化：高效的数据结构和算法

        注意事项:
        - 只能更新已存在的设置项，不存在的key会被记录为失败
        - key字段用于定位要更新的设置项，不能修改key本身
        - 当settingType为json时，会对value进行JSON格式校验
        - 如果不提供可选字段，则保持原值不变
        - 建议在批量更新前先通过查询接口确认要更新的设置项存在

        使用示例:
        PUT /system/settings/batch
        {
            "settings": [
                {
                    "key": "email_smtp_host",
                    "value": "smtp.newserver.com",
                    "settingType": "string",
                    "group": "email",
                    "description": "更新后的邮件服务器地址"
                },
                {
                    "key": "notification_config",
                    "value": "{\"email\": true, \"sms\": false}",
                    "settingType": "json",
                    "description": "通知配置"
                },
                {
                    "key": "max_login_attempts",
                    "value": "5",
                    "settingType": "int",
                    "group": "security"
                }
            ]
        }
        """
        debug("批量更新系统设置，开始")

        try:
            # 使用 api.payload 获取已校验的数据
            json_data: Dict[str, Any] = api_ns.payload
            debug(f"批量更新系统设置，参数：{json_data}")

            # 获取设置项列表
            settings_data: List[Dict[str, Any]] = json_data.get('settings', [])
            
            if len(settings_data) > 50:
                return R.fail(msg="单次批量更新最多支持50个设置项")

            # 使用批量更新服务
            batch_service = SystemSettingsBatchService(db.session)
            result: Dict[str, Any] = batch_service.batch_update_settings(settings_data)

            # 构建响应消息
            success_count: int = result['success_count']
            failure_count: int = result['failure_count']

            if failure_count == 0:
                message: str = f"批量更新完成，成功更新 {success_count} 个设置项"
                debug(f"批量更新系统设置完成：{message}")
                return R.ok(data=result, msg=message)
            elif success_count == 0:
                message = f"批量更新失败，{failure_count} 个设置项更新失败"
                debug(f"批量更新系统设置完成：{message}")
                return R.fail(data=result, msg=message)
            else:
                message = f"批量更新部分成功，成功 {success_count} 个，失败 {failure_count} 个"
                debug(f"批量更新系统设置完成：{message}")
                return R.ok(data=result, msg=message)

        except Exception as e:
            db.session.rollback()
            error(f"批量更新系统设置失败：{str(e)}")
            return R.fail(msg=f"批量更新失败：{str(e)}")
