from flask_restx import Namespace, Resource
from flask import request
from marshmallow import ValidationError

from web.common.api_factory import get_api
from web.common.utils import R
from web.models import db
from web.models.asset.asset_alias import AssetAlias, AssetAliasSchema
from sqlalchemy.orm import joinedload
from web.weblogger import info, error
from .asset_alias_list_schemas import create_asset_alias_list_models, AssetAliasListQuerySchema


api = get_api()
api_ns = Namespace("asset_alias_list", description="资产别名列表与批量接口")
if api:
    api.add_namespace(api_ns, path="/api/asset/alias")

models = create_asset_alias_list_models(api_ns)
list_response_model = models["list_response_model"]
base_response_model = models["base_response_model"]
batch_associate_request_model = models["batch_associate_request_model"]



@api_ns.route("/list")
class AssetAliasListRouters(Resource):
    @api_ns.marshal_with(list_response_model)
    def get(self):
        """
        分页查询资产别名列表

        1. 路径参数说明
        - 无

        2. 返回数据格式
        - 成功响应格式：{"code": 20000, "data": {"items": [...], "total": 100, "page": 1, "size": 20}, "message": "查询成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        3. 数据格式说明
        - 过滤参数支持：`providerCode`（模糊匹配）、`providerSymbol`（模糊匹配）、`status`（0/1）、`isPrimary`（0/1）
        - 字段命名：API使用驼峰命名；返回时间字段使用 yyyy-MM-dd HH:mm:ss 格式
        - 布尔字段：`isPrimary` 为布尔类型
        - 关联字段：返回 `assetName`（资产名称）用于直观展示归属资产

        4. 关键注意事项
        - 分页参数 `page/pageSize` 必填，`page` 从 1 开始
        - 查询结果按 `id` 排序

        5. 请求示例
        - GET /api/asset/alias/list?page=1&pageSize=20&providerCode=xq&status=1

        6. 返回示例
        - 成功响应：
          {"code":20000,"success":true,"message":"查询成功","data":{"items":[{"id":1,"assetId":123,"assetName":"招商银行","providerCode":"xq","providerSymbol":"600036","providerName":"招商银行","isPrimary":true,"status":1,"createTime":"2025-01-01 10:00:00","updateTime":"2025-01-10 10:00:00"}],"total":1,"page":1,"size":20}}
        - 失败响应：
          {"code":20500,"success":false,"message":"查询资产别名列表失败: Database error","data":false}
        """
        try:
            raw = request.args.to_dict()
            schema = AssetAliasListQuerySchema()
            try:
                args = schema.load(raw)
            except ValidationError as ve:
                return R.fail(msg=f"参数验证失败: {ve.messages}", data=ve.messages)

            page = args.get("page")
            page_size = args.get("pageSize")
            provider_code = args.get("providerCode")
            provider_symbol = args.get("providerSymbol")
            status = args.get("status")
            is_primary = args.get("isPrimary")

            conditions = []
            if provider_code:
                conditions.append(AssetAlias.provider_code.like(f"%{provider_code}%"))
            if provider_symbol:
                conditions.append(AssetAlias.provider_symbol.like(f"%{provider_symbol}%"))
            if status is not None:
                conditions.append(AssetAlias.status == status)
            if is_primary is not None:
                conditions.append(AssetAlias.is_primary == bool(is_primary))

            result = (
                AssetAlias.query.options(joinedload(AssetAlias.asset))
                .filter(*conditions)
                .order_by(AssetAlias.id)
                .paginate(page=page, per_page=page_size, error_out=False)
            )
            items = AssetAliasSchema().dump(result.items, many=True)
            for i, alias in enumerate(result.items):
                asset_name = alias.asset.asset_name if getattr(alias, "asset", None) else None
                items[i].update({"assetName": asset_name})
            return R.paginate(data=items, total=result.total, page=page, size=page_size, msg="查询成功")
        except Exception as e:
            error(f"查询资产别名列表失败: {str(e)}", exc_info=True)
            return R.fail(msg=f"查询资产别名列表失败: {str(e)}")


@api_ns.route("/batch-associate")
class AssetAliasBatchAssociateRouters(Resource):
    @api_ns.expect(batch_associate_request_model, validate=False)
    @api_ns.marshal_with(base_response_model)
    def put(self):
        """
        批量关联资产：将多个别名关联到指定资产

        1. 路径参数说明
        - 无

        2. 返回数据格式
        - 成功响应格式：{"code": 20000, "data": true, "message": "批量关联成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        3. 数据格式说明
        - 请求体字段：`assetId`（目标资产ID，必填）、`aliasIds`（别名ID列表，必填）
        - 行为：将列表中的别名的 `assetId` 更新为目标资产ID，不修改 `isPrimary`

        4. 关键注意事项
        - `aliasIds` 为空将返回失败
        - 遇到不存在的别名ID将跳过处理
        - 操作失败自动回滚事务

        5. 请求示例
        - PUT /api/asset/alias/batch-associate
        - Body：{"assetId":123,"aliasIds":[1,2,3]}

        6. 返回示例
        - 成功响应：{"code":20000,"success":true,"message":"批量关联成功","data":true}
        - 失败响应：{"code":20500,"success":false,"message":"批量关联资产失败: Database error","data":false}
        """
        try:
            data = api.payload or {}
            asset_id = data.get("assetId")
            alias_ids = data.get("aliasIds") or []

            if not asset_id:
                return R.fail(msg="assetId 为必填字段")
            if not alias_ids:
                return R.fail(msg="aliasIds 不能为空")

            aliases = AssetAlias.query.filter(AssetAlias.id.in_(alias_ids)).all()
            for alias in aliases:
                alias.asset_id = asset_id

            db.session.commit()
            info(f"批量关联资产成功，资产ID: {asset_id}，别名数量: {len(aliases)}")
            return R.ok(data=True, msg="批量关联成功")
        except Exception as e:
            db.session.rollback()
            error(f"批量关联资产失败: {str(e)}", exc_info=True)
            return R.fail(msg=f"批量关联资产失败: {str(e)}")