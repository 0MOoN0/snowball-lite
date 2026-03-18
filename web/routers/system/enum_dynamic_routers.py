# -*- coding: UTF-8 -*-
"""
@File    ：enum_dynamic_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27
@Description: 动态枚举接口，支持根据枚举键名获取对应枚举的序列化数据
"""

from flask_restx import Resource, Namespace, fields
from web.common.api_factory import get_api
from web.common.utils import R
from web.common.enum.enum_registry import EnumRegistry
from web.common.utils.enum_utils import serialize_enum
from web.weblogger import debug, error

# 创建Namespace
api_ns = Namespace("enum_dynamic", description="动态枚举接口")

# 获取全局API实例并注册namespace
api = get_api()
if api:
    api.add_namespace(api_ns, path="/api/enums")

# 定义响应模型
enum_item_model = api_ns.model(
    "EnumItem",
    {
        "value": fields.Raw(description="枚举值"),
        "label": fields.String(description="枚举标签"),
    },
)

enum_response_model = api_ns.model(
    "EnumResponse",
    {
        "code": fields.Integer(description="响应代码"),
        "success": fields.Boolean(description="是否成功"),
        "message": fields.String(description="响应消息"),
        "data": fields.List(fields.Nested(enum_item_model), description="枚举数据列表"),
    },
)

available_enums_response_model = api_ns.model(
    "AvailableEnumsResponse",
    {
        "code": fields.Integer(description="响应代码"),
        "success": fields.Boolean(description="是否成功"),
        "message": fields.String(description="响应消息"),
        "data": fields.Raw(description="可用枚举列表，键为枚举名，值为描述"),
    },
)

# 批量获取枚举请求模型
batch_enum_request_model = api_ns.model(
    "BatchEnumRequest",
    {
        "enumKeys": fields.List(
            fields.String(),
            required=True,
            description="要获取的枚举键名列表",
            min_items=1,
        )
    },
)

# 批量枚举数据项模型
batch_enum_data_item_model = api_ns.model(
    "BatchEnumDataItem",
    {
        "enumKey": fields.String(description="枚举键名"),
        "data": fields.List(fields.Nested(enum_item_model), description="枚举数据列表"),
        "success": fields.Boolean(description="该枚举是否获取成功"),
        "message": fields.String(description="获取结果消息"),
    },
)

# 批量获取枚举响应模型
batch_enum_response_model = api_ns.model(
    "BatchEnumResponse",
    {
        "code": fields.Integer(description="响应代码"),
        "success": fields.Boolean(description="是否成功"),
        "message": fields.String(description="响应消息"),
        "data": fields.Nested(
            api_ns.model(
                "BatchEnumResponseData",
                {
                    "successCount": fields.Integer(description="成功获取的枚举数量"),
                    "failureCount": fields.Integer(description="获取失败的枚举数量"),
                    "results": fields.List(
                        fields.Nested(batch_enum_data_item_model),
                        description="批量获取结果列表",
                    ),
                },
            ),
            description="批量获取结果数据",
        ),
    },
)


@api_ns.route("/<string:enum_key>")
class EnumDynamicRouters(Resource):
    @api_ns.doc("get_enum_by_key")
    @api_ns.marshal_with(enum_response_model)
    def get(self, enum_key: str):
        """
        根据枚举键名获取枚举序列化数据

        - enum_key (string, required): 枚举类名，如 'CurrencyEnum'、'AssetTypeEnum' 等

        返回数据格式:
        - 成功响应格式：{"code": 20000, "data": [{"value": 0, "label": "人民币"}, {"value": 1, "label": "美元"}, ...], "message": "获取枚举数据成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": [], "message": "错误信息", "success": false}

        数据格式说明:
        - 返回数据为数组格式，每个元素包含 value（枚举值）和 label（显示标签）
        - 标签优先使用 @register_labels_by_name 装饰器注册的中文标签，否则使用枚举成员名

        关键注意事项:
        - 枚举键名必须在注册表中存在，否则返回失败响应
        - 支持的枚举类型包括通用枚举、资产枚举、基金枚举、指数枚举等
        - 返回顺序与枚举定义顺序一致

        请求示例:
        GET /api/enums/CurrencyEnum

        返回示例:
        成功响应:
        {
            "code": 20000,
            "success": true,
            "message": "获取枚举数据成功",
            "data": [
                {"value": 0, "label": "人民币"},
                {"value": 1, "label": "美元"},
                {"value": 2, "label": "欧元"},
                {"value": 3, "label": "港币"}
            ]
        }

        失败响应:
        {
            "code": 20500,
            "success": false,
            "message": "枚举键 'InvalidEnum' 不存在",
            "data": []
        }
        """
        try:
            debug(f"开始获取枚举数据，枚举键: {enum_key}")

            # 检查枚举键是否有效
            if not EnumRegistry.is_valid_enum_key(enum_key):
                error(f"无效的枚举键: {enum_key}")
                return R.fail(msg=f"枚举键 '{enum_key}' 不存在")

            # 获取枚举类
            enum_class = EnumRegistry.get_enum_class(enum_key)
            debug(f"成功获取枚举类: {enum_class.__name__}")

            # 序列化枚举数据
            enum_data = serialize_enum(enum_class)
            debug(f"成功序列化枚举数据，共 {len(enum_data)} 个成员")

            return R.ok(data=enum_data, msg="获取枚举数据成功")

        except KeyError as e:
            error(f"枚举键不存在: {e}", exc_info=True)
            return R.fail(msg=f"枚举键 '{enum_key}' 不存在")
        except Exception as e:
            error(f"获取枚举数据失败: {e}", exc_info=True)
            return R.fail(msg="获取枚举数据失败")


@api_ns.route("/")
class AvailableEnumsRouters(Resource):
    @api_ns.doc("get_available_enums")
    @api_ns.marshal_with(available_enums_response_model)
    def get(self):
        """
        获取所有可用的枚举列表

        返回数据格式:
        - 成功响应格式：{"code": 20000, "data": {"CurrencyEnum": "货币类型枚举", "AssetTypeEnum": "资产类型枚举", ...}, "message": "获取可用枚举列表成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": {}, "message": "错误信息", "success": false}

        数据格式说明:
        - 返回数据为对象格式，键为枚举类名，值为枚举描述
        - 描述信息来源于枚举类的文档字符串

        关键注意事项:
        - 返回系统中所有已注册的枚举类信息
        - 可用于前端动态生成枚举选择器或文档

        请求示例:
        GET /api/enums/

        返回示例:
        成功响应:
        {
            "code": 20000,
            "success": true,
            "message": "获取可用枚举列表成功",
            "data": {
                "CurrencyEnum": "货币类型枚举",
                "AssetTypeEnum": "资产类型枚举，包括：指数，基金，股票等",
                "FundTypeEnum": "基金投资策略类型枚举"
            }
        }

        失败响应:
        {
            "code": 20500,
            "success": false,
            "message": "获取可用枚举列表失败",
            "data": {}
        }
        """
        try:
            debug("开始获取可用枚举列表")

            # 获取所有可用枚举
            available_enums = EnumRegistry.get_available_enums()
            debug(f"成功获取可用枚举列表，共 {len(available_enums)} 个枚举")

            return R.ok(data=available_enums, msg="获取可用枚举列表成功")

        except Exception as e:
            error(f"获取可用枚举列表失败: {e}", exc_info=True)
            return R.fail(msg="获取可用枚举列表失败")


@api_ns.route("/batch")
class BatchEnumRouters(Resource):
    @api_ns.doc("batch_get_enums")
    @api_ns.expect(batch_enum_request_model)
    @api_ns.marshal_with(batch_enum_response_model)
    def post(self):
        """
        批量获取枚举数据接口

        支持一次性获取多个枚举的序列化数据，采用部分成功策略，即使部分枚举获取失败，
        其他成功的枚举数据仍会返回。适用于前端批量初始化枚举数据等场景。

        核心特性:
        - 部分成功策略：单个枚举获取失败不影响其他枚举的获取
        - 详细结果报告：返回每个枚举的获取状态和数据
        - 高性能：批量处理减少网络请求次数
        - 类型安全：完整的类型提示和数据验证
        - 数量限制：单次最多获取20个枚举，防止系统过载

        请求体参数:
        - enumKeys (array, required): 要获取的枚举键名列表，最多20项
          - 每个元素为字符串类型，如 'CurrencyEnum'、'AssetTypeEnum' 等
          - 枚举键名必须在系统注册表中存在

        返回数据格式:
        - 成功响应格式：{"code": 20000, "data": {...}, "message": "批量获取完成", "success": true}
        - 失败响应格式：{"code": 20500, "data": {...}, "message": "错误信息", "success": false}

        数据格式说明:
        - successCount (int): 成功获取的枚举数量
        - failureCount (int): 获取失败的枚举数量
        - results (array): 批量获取结果列表
          - enumKey (string): 枚举键名
          - data (array): 枚举数据列表，格式与单个枚举接口一致
          - success (boolean): 该枚举是否获取成功
          - message (string): 获取结果消息

        关键注意事项:
        - 只能获取已在注册表中存在的枚举，不存在的枚举会被记录为失败
        - 返回的枚举数据格式与单个枚举接口保持一致
        - 建议在批量获取前先通过可用枚举列表接口确认要获取的枚举存在
        - 单次请求最多支持20个枚举，超出限制会返回错误

        请求示例:
        POST /api/enums/batch
        {
            "enumKeys": ["CurrencyEnum", "AssetTypeEnum", "FundTypeEnum"]
        }

        返回示例:
        成功响应:
        {
            "code": 20000,
            "success": true,
            "message": "批量获取完成，成功获取 2 个枚举",
            "data": {
                "successCount": 2,
                "failureCount": 1,
                "results": [
                    {
                        "enumKey": "CurrencyEnum",
                        "data": [
                            {"value": 0, "label": "人民币"},
                            {"value": 1, "label": "美元"}
                        ],
                        "success": true,
                        "message": "获取枚举数据成功"
                    },
                    {
                        "enumKey": "AssetTypeEnum",
                        "data": [
                            {"value": 0, "label": "指数"},
                            {"value": 1, "label": "基金"}
                        ],
                        "success": true,
                        "message": "获取枚举数据成功"
                    },
                    {
                        "enumKey": "InvalidEnum",
                        "data": [],
                        "success": false,
                        "message": "枚举键 'InvalidEnum' 不存在"
                    }
                ]
            }
        }

        失败响应:
        {
            "code": 20500,
            "success": false,
            "message": "批量获取失败，所有枚举获取失败",
            "data": {
                "successCount": 0,
                "failureCount": 2,
                "results": [...]
            }
        }
        """
        try:
            debug("开始批量获取枚举数据")

            # 使用 api_ns.payload 获取已校验的数据
            json_data = api_ns.payload
            debug(f"批量获取枚举数据，参数：{json_data}")

            # 获取枚举键名列表
            enum_keys = json_data.get("enumKeys", [])

            # if len(enum_keys) > 20:
            #     return R.fail(msg="单次批量获取最多支持20个枚举")

            # 初始化结果统计
            success_count = 0
            failure_count = 0
            results = []

            # 逐个处理枚举获取
            for enum_key in enum_keys:
                try:
                    debug(f"处理枚举：{enum_key}")

                    # 检查枚举键是否有效
                    if not EnumRegistry.is_valid_enum_key(enum_key):
                        error(f"无效的枚举键: {enum_key}")
                        results.append(
                            {
                                "enumKey": enum_key,
                                "data": [],
                                "success": False,
                                "message": f"枚举键 '{enum_key}' 不存在",
                            }
                        )
                        failure_count += 1
                        continue

                    # 获取枚举类并序列化
                    enum_class = EnumRegistry.get_enum_class(enum_key)
                    enum_data = serialize_enum(enum_class)

                    results.append(
                        {
                            "enumKey": enum_key,
                            "data": enum_data,
                            "success": True,
                            "message": "获取枚举数据成功",
                        }
                    )
                    success_count += 1
                    debug(f"成功获取枚举 {enum_key}，数据量：{len(enum_data)}")

                except KeyError as e:
                    error(f"枚举键不存在: {enum_key}, {e}", exc_info=True)
                    results.append(
                        {
                            "enumKey": enum_key,
                            "data": [],
                            "success": False,
                            "message": f"枚举键 '{enum_key}' 不存在",
                        }
                    )
                    failure_count += 1
                except Exception as e:
                    error(f"获取枚举 {enum_key} 失败: {e}", exc_info=True)
                    results.append(
                        {
                            "enumKey": enum_key,
                            "data": [],
                            "success": False,
                            "message": f"获取枚举数据失败：{str(e)}",
                        }
                    )
                    failure_count += 1

            # 构建响应数据
            response_data = {
                "successCount": success_count,
                "failureCount": failure_count,
                "results": results,
            }

            # 构建响应消息
            if failure_count == 0:
                message = f"批量获取完成，成功获取 {success_count} 个枚举"
                debug(f"批量获取枚举完成：{message}")
                return R.ok(data=response_data, msg=message)
            elif success_count == 0:
                message = f"批量获取失败，{failure_count} 个枚举获取失败"
                debug(f"批量获取枚举完成：{message}")
                return R.fail(data=response_data, msg=message)
            else:
                message = f"批量获取部分成功，成功 {success_count} 个，失败 {failure_count} 个"
                debug(f"批量获取枚举完成：{message}")
                return R.ok(data=response_data, msg=message)

        except Exception as e:
            error(f"批量获取枚举数据失败: {e}", exc_info=True)
            return R.fail(msg=f"批量获取失败：{str(e)}")
