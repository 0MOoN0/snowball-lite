from flask_restx import Namespace, Resource
from marshmallow import ValidationError

from web.common.api_factory import get_api
from web.common.utils import R
from web.models import db
from web.models.asset.asset_alias import AssetAlias, AssetAliasSchema
from sqlalchemy.orm import joinedload
from web.weblogger import info, warning, error
from .asset_alias_detail_schemas import (
    create_asset_alias_detail_models,
    AssetAliasCreateSchema,
    AssetAliasUpdateSchema,
)


api = get_api()
api_ns = Namespace("asset_alias", description="资产别名管理接口")
if api:
    api.add_namespace(api_ns, path="/api/asset/alias")

models = create_asset_alias_detail_models(api_ns)
single_alias_response_model = models["single_alias_response_model"]
base_response_model = models["base_response_model"]
alias_create_request_model = models["alias_create_request_model"]
alias_update_request_model = models["alias_update_request_model"]


@api_ns.route("/<int:alias_id>")
class AssetAliasDetailRouters(Resource):
    @api_ns.marshal_with(single_alias_response_model)
    def get(self, alias_id: int):
        """
        根据ID获取资产别名详情

        1. 路径参数说明
        - alias_id (int, required): 资产别名的唯一标识ID

        2. 返回数据格式
        - 成功响应格式：{"code": 20000, "data": {Alias}, "message": "查询成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        3. 数据格式说明
        - 字段命名：API使用驼峰命名（如 providerCode/providerSymbol），数据库使用下划线命名，自动转换
        - 布尔字段：`isPrimary` 为布尔类型
        - 时间字段：`createTime`、`updateTime` 使用 yyyy-MM-dd HH:mm:ss 格式字符串
        - 关联字段：返回 `assetName`（资产名称）用于直观展示归属资产

        4. 关键注意事项
        - 仅返回启用状态（status=1）的别名；未启用或不存在返回失败响应
        - 不进行任何状态变更或唯一性检查，仅查询

        5. 请求示例
        - GET /api/asset/alias/1

        6. 返回示例
        - 成功响应：
          {"code":20000,"success":true,"message":"查询成功","data":{"id":1,"assetId":123,"assetName":"招商银行","providerCode":"xq","providerSymbol":"600036","providerName":"招商银行","isPrimary":true,"status":1,"createTime":"2025-01-01 10:00:00","updateTime":"2025-01-10 10:00:00"}}
        - 失败响应：
          {"code":20500,"success":false,"message":"资产别名不存在或未启用，ID: 999","data":false}
        """
        try:
            info(f"查询资产别名详情，ID: {alias_id}")
            alias: AssetAlias | None = AssetAlias.query.options(joinedload(AssetAlias.asset)).filter_by(id=alias_id).first()
            if not alias or alias.status != 1:
                warning(f"资产别名不存在或未启用，ID: {alias_id}")
                return R.fail(msg=f"资产别名不存在或未启用，ID: {alias_id}")

            data = AssetAliasSchema().dump(alias)
            try:
                asset_name = alias.asset.asset_name if alias.asset else None
            except Exception:
                asset_name = None
            if asset_name is not None:
                data.update({"assetName": asset_name})
            return R.ok(data=data, msg="查询成功")
        except Exception as e:
            error(f"查询资产别名失败，ID: {alias_id}, 错误: {str(e)}", exc_info=True)
            return R.fail(msg=f"查询资产别名失败: {str(e)}")

    @api_ns.expect(alias_update_request_model, validate=False)
    @api_ns.marshal_with(single_alias_response_model)
    def put(self, alias_id: int):
        """
        根据ID更新资产别名

        1. 路径参数说明
        - alias_id (int, required): 资产别名的唯一标识ID

        2. 返回数据格式
        - 成功响应格式：{"code": 20000, "data": {Alias}, "message": "更新成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        3. 数据格式说明
        - 请求体字段（驼峰命名）：允许更新 `providerCode`、`providerSymbol`、`providerName`、`isPrimary`、`description`、`status`、`assetId`
        - 唯一约束：`providerCode + providerSymbol` 在系统中全局唯一；更新为重复组合将失败
        - 主别名：当 `isPrimary=1` 时，会自动取消同资产其它别名的主标记，保证唯一
        - `isPrimary` 仅支持整型 `0/1`
        - 时间字段返回格式：yyyy-MM-dd HH:mm:ss

        4. 关键注意事项
        - 不存在的 `alias_id` 返回失败
        - 当修改 `providerCode/providerSymbol` 时执行唯一性预检
        - 更新 `assetId` 会更改该别名的归属资产

        5. 请求示例
        - PUT /api/asset/alias/1
        - Body：{"providerCode":"xq","providerSymbol":"600036","providerName":"招商银行","isPrimary":1,"description":"主交易代码"}

        6. 返回示例
        - 成功响应：
          {"code":20000,"success":true,"message":"更新成功","data":{"id":1,"assetId":123,"providerCode":"xq","providerSymbol":"600036","providerName":"招商银行","isPrimary":true,"status":1,"createTime":"2025-01-01T10:00:00","updateTime":"2025-01-10T10:00:00"}}
        - 失败响应（唯一冲突）：
          {"code":20500,"success":false,"message":"该提供商代码与符号已存在，不能重复","data":false}
        """
        try:
            data = api.payload or {}
            alias: AssetAlias | None = AssetAlias.query.get(alias_id)
            if not alias:
                return R.fail(msg=f"资产别名不存在，ID: {alias_id}")

            schema = AssetAliasUpdateSchema()
            try:
                loaded = schema.load(data)
            except ValidationError as ve:
                return R.fail(msg=f"数据验证失败: {ve.messages}", data=ve.messages)

            provider_code = loaded.get("provider_code")
            provider_symbol = loaded.get("provider_symbol")
            provider_name = loaded.get("provider_name")
            description = loaded.get("description")
            status = loaded.get("status")
            is_primary_int = loaded.get("is_primary")
            asset_id = loaded.get("asset_id")

            if provider_code is not None or provider_symbol is not None:
                new_code = provider_code if provider_code is not None else alias.provider_code
                new_symbol = provider_symbol if provider_symbol is not None else alias.provider_symbol
                exists = db.session.query(AssetAlias).filter(
                    AssetAlias.provider_code == new_code,
                    AssetAlias.provider_symbol == new_symbol,
                    AssetAlias.id != alias_id,
                ).first()
                if exists:
                    return R.fail(msg="该提供商代码与符号已存在，不能重复")

            if provider_code is not None:
                alias.provider_code = provider_code
            if provider_symbol is not None:
                alias.provider_symbol = provider_symbol
            if provider_name is not None:
                alias.provider_name = provider_name
            if description is not None:
                alias.description = description
            if status is not None:
                alias.status = status
            if asset_id is not None:
                alias.asset_id = asset_id

            if is_primary_int is not None:
                alias.is_primary = True if is_primary_int == 1 else False
                if alias.is_primary:
                    db.session.query(AssetAlias).filter(
                        AssetAlias.asset_id == alias.asset_id,
                        AssetAlias.id != alias.id,
                    ).update({AssetAlias.is_primary: False}, synchronize_session=False)

            db.session.commit()
            info(f"更新资产别名成功，ID: {alias_id}")
            return R.ok(data=AssetAliasSchema().dump(alias), msg="更新成功")
        except Exception as e:
            db.session.rollback()
            error(f"更新资产别名失败，ID: {alias_id}, 错误: {str(e)}", exc_info=True)
            return R.fail(msg=f"更新资产别名失败: {str(e)}")

    @api_ns.marshal_with(base_response_model)
    def delete(self, alias_id: int):
        """
        删除资产别名（硬删除）

        1. 路径参数说明
        - alias_id (int, required): 资产别名的唯一标识ID

        2. 返回数据格式
        - 成功响应格式：{"code": 20000, "data": true, "message": "删除成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        3. 数据格式说明
        - 硬删除：直接移除数据库记录，不保留历史；无需处理主别名标记

        4. 关键注意事项
        - 不存在的 `alias_id` 返回失败
        - 删除为不可恢复操作，请谨慎执行
        - 时间字段返回格式：yyyy-MM-dd HH:mm:ss

        5. 请求示例
        - DELETE /api/asset/alias/1

        6. 返回示例
        - 成功响应：{"code":20000,"success":true,"message":"删除成功","data":true}
        - 失败响应：{"code":20500,"success":false,"message":"资产别名不存在，ID: 999","data":false}
        """
        try:
            alias: AssetAlias | None = AssetAlias.query.get(alias_id)
            if not alias:
                return R.fail(msg=f"资产别名不存在，ID: {alias_id}")

            db.session.delete(alias)
            db.session.commit()
            info(f"删除资产别名成功，ID: {alias_id}")
            return R.ok(data=True, msg="删除成功")
        except Exception as e:
            db.session.rollback()
            error(f"删除资产别名失败，ID: {alias_id}, 错误: {str(e)}", exc_info=True)
            return R.fail(msg=f"删除资产别名失败: {str(e)}")


@api_ns.route("/")
class AssetAliasCreateRouters(Resource):
    @api_ns.expect(alias_create_request_model, validate=False)
    @api_ns.marshal_with(single_alias_response_model)
    def post(self):
        """
        新增资产别名

        1. 路径参数说明
        - 无

        2. 返回数据格式
        - 成功响应格式：{"code": 20000, "data": {Alias}, "message": "新增成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        3. 数据格式说明
        - 必填字段：`assetId`、`providerCode`、`providerSymbol`
        - 可选字段：`providerName`、`isPrimary`、`description`、`status`
        - 唯一约束：`providerCode + providerSymbol` 全局唯一
        - 主别名：当 `isPrimary=1` 时，取消同资产其它别名的主标记
        - `isPrimary` 仅支持整型 `0/1`

        4. 关键注意事项
        - 若唯一约束冲突则新增失败
        - `status` 默认 `1`（启用）

        5. 请求示例
        - POST /api/asset/alias
        - Body：{"assetId":123,"providerCode":"xq","providerSymbol":"600036","providerName":"招商银行","isPrimary":1}

        6. 返回示例
        - 成功响应：
          {"code":20000,"success":true,"message":"新增成功","data":{"id":10,"assetId":123,"providerCode":"xq","providerSymbol":"600036","providerName":"招商银行","isPrimary":true,"status":1,"createTime":"2025-01-20T10:00:00","updateTime":"2025-01-20T10:00:00"}}
        - 失败响应（唯一冲突）：
          {"code":20500,"success":false,"message":"该提供商代码与符号已存在，不能重复","data":false}
        """
        try:
            data = api.payload or {}

            schema = AssetAliasCreateSchema()
            try:
                loaded = schema.load(data)
            except ValidationError as ve:
                return R.fail(msg=f"数据验证失败: {ve.messages}", data=ve.messages)

            asset_id = loaded.get("asset_id")
            provider_code = loaded.get("provider_code")
            provider_symbol = loaded.get("provider_symbol")
            provider_name = loaded.get("provider_name")
            is_primary_val = loaded.get("is_primary")
            is_primary = bool(is_primary_val) if is_primary_val is not None else False
            status_val = loaded.get("status")
            status = status_val if status_val is not None else 1
            description = loaded.get("description")

            exists = db.session.query(AssetAlias).filter(
                AssetAlias.provider_code == provider_code,
                AssetAlias.provider_symbol == provider_symbol,
            ).first()
            if exists:
                return R.fail(msg="该提供商代码与符号已存在，不能重复")

            alias = AssetAlias(
                asset_id=asset_id,
                provider_code=provider_code,
                provider_symbol=provider_symbol,
                provider_name=provider_name,
                is_primary=is_primary,
                status=status,
                description=description,
            )

            db.session.add(alias)
            db.session.flush()

            if alias.is_primary:
                db.session.query(AssetAlias).filter(
                    AssetAlias.asset_id == alias.asset_id,
                    AssetAlias.id != alias.id,
                ).update({AssetAlias.is_primary: False}, synchronize_session=False)

            db.session.commit()
            info(f"新增资产别名成功，ID: {alias.id}")
            return R.ok(data=AssetAliasSchema().dump(alias), msg="新增成功")
        except Exception as e:
            db.session.rollback()
            error(f"新增资产别名失败，错误: {str(e)}", exc_info=True)
            return R.fail(msg=f"新增资产别名失败: {str(e)}")