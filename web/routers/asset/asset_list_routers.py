# -*- coding: UTF-8 -*-
"""
@File    ：asset_list_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/21 10:00
@Description: 资产列表管理接口 - 使用Flask-RestX实现
"""

from decimal import Decimal

from flask_marshmallow import Schema
from flask import request
from flask_restx import Namespace, Resource, reqparse
from marshmallow import fields, post_dump, ValidationError

from web.common.api_factory import get_api
from web.common.utils import R
from web.models import db
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.models.asset.asset import Asset, AssetListQuerySchema
from web.models.asset.asset_alias import AssetAlias
from web.models.asset.asset_category import AssetCategory
from web.models.asset.asset_code import AssetCode
from web.models.category.Category import Category
from web.models.grid.Grid import Grid
from web.weblogger import debug, error
from .asset_list_schemas import create_asset_list_models, AssetListRequestSchema
from .asset_select_schemas import AssetSelectQuerySchema
from web.common.enum.asset_enum import AssetTypeEnum

# 创建并注册namespace
api = get_api()
api_ns = Namespace("asset_list", description="资产列表管理接口")
if api:
    api.add_namespace(api_ns, path="/api/asset/list")

# 创建模型
asset_list_models = create_asset_list_models(api_ns)

asset_list_response_model = asset_list_models["asset_list_response_model"]
asset_delete_model = asset_list_models["asset_delete_model"]
asset_delete_response_model = asset_list_models["asset_delete_response_model"]


@api_ns.route("/")
class AssetListRouters(Resource):
    """资产列表路由类"""



    @api_ns.doc("get_asset_list")
    # @api_ns.expect(query_parser) # 移除reqparse文档装饰器，因为改用了Marshmallow
    @api_ns.marshal_with(asset_list_response_model)
    def get(self):
        """
        资产列表查询接口

        根据资产名称、资产类型和网格ID查询资产列表信息，支持分页查询。
        仅查询Asset基础对象，关联AssetFundDailyData获取收盘价和涨跌幅信息。

        请求参数:
        - page (int, required): 页码，从1开始
        - pageSize (int, required): 每页条数，建议范围1-100
        - assetName (string, optional): 资产名称，支持模糊匹配
        - assetType (string, optional): 资产类型，支持多态查询（如查询基金会自动包含ETF、LOF）
        - gridId (string, optional): 网格ID，用于查询特定网格关联的资产

        返回数据格式:
        - 成功响应格式：{"code": 20000, "data": {"items": [...], "total": 100, "page": 1, "size": 20}, "message": "查询成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        数据格式说明:
        - 仅包含Asset基础字段和AssetFundDailyData的收盘价、涨跌幅信息
        - 价格字段（close、closePercent）返回原始数值，未进行格式化处理
        - 最新数据：返回资产的最新交易日数据

        关键注意事项:
        - 支持多态查询：查询父类（如基金）会自动包含所有子类（如ETF、LOF）
        - 不连接asset_code表
        - 查询结果按资产ID排序，确保数据一致性
        - 网格ID查询时会验证网格是否存在

        请求示例:
        GET /api/asset/list?page=1&pageSize=20&assetName=招商银行

        返回示例:
        {
            "code": 20000,
            "data": {
                "items": [
                    {
                        "id": 1,
                        "assetCode": "600036",
                        "assetShortCode": "ZSYH",
                        "assetStatus": 0,
                        "currency": 0,
                        "assetType": 2,
                        "assetName": "招商银行",
                        "market": 0,
                        "date": "2024-01-15",
                        "close": "12345",
                        "closePercent": "123"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 20
            },
            "message": "查询成功",
            "success": true
        }
        """
        debug("查询资产列表，开始")

        # 解析查询参数
        try:
            # 使用Marshmallow Schema解析参数
            raw_args = request.args.to_dict()
            args = AssetListRequestSchema().load(raw_args)
            debug(f"查询资产列表，参数：{args}")
            
            page = args.get("page")
            page_size = args.get("page_size")
            condition = []
            
            # 构建查询条件
            if args.get("asset_name") is not None:
                condition.append(
                    Asset.asset_name.like("%" + args.get("asset_name") + "%")
                )
            
            # 确定查询的目标模型
            target_model = Asset
            if args.get("asset_type") is not None:
                asset_type_val = int(args.get("asset_type"))
                # 使用Asset模型中封装的方法获取多态模型
                target_model = Asset.get_polymorphic_model(asset_type_val)
            
            if args.get("grid_id") is not None:
                grid: Grid = Grid.query.get(args.get("grid_id"))
                if grid:
                    condition.append(Asset.id == grid.asset_id)
                else:
                    return R.fail(msg="网格不存在")
            
            # 创建AssetFundDailyData子查询，获取每个资产的最新数据
            daily_alias = db.aliased(AssetFundDailyData)
            subq = (
                db.session.query(
                    daily_alias.asset_id,
                    db.func.max(daily_alias.f_date).label("max_date"),
                )
                .group_by(daily_alias.asset_id)
                .subquery()
            )
            
            # 创建第二个子查询，用于查询最新的资产日线数据
            daily_subq = (
                db.session.query(
                    AssetFundDailyData.f_date,
                    AssetFundDailyData.asset_id,
                    AssetFundDailyData.f_close,
                    AssetFundDailyData.f_close_percent,
                )
                .join(
                    subq,
                    db.and_(
                        AssetFundDailyData.asset_id == subq.c.asset_id,
                        AssetFundDailyData.f_date == subq.c.max_date,
                    ),
                )
                .subquery()
            )
            
            # 主查询：查询目标模型（可能是Asset或其子类），关联AssetFundDailyData
            # 关联AssetAlias获取主要别名
            # 注意：使用target_model.id可以让SQLAlchemy自动处理多态查询
            result = (
                db.session.query(
                    target_model.id,
                    AssetAlias.provider_symbol.label("asset_code"),
                    target_model.asset_status,
                    target_model.currency,
                    target_model.asset_type,
                    target_model.asset_name,
                    target_model.market,
                    daily_subq.c.f_date,
                    daily_subq.c.f_close,
                    daily_subq.c.f_close_percent,
                )
                .join(daily_subq, target_model.id == daily_subq.c.asset_id, isouter=True)
                .join(
                    AssetAlias,
                    db.and_(
                        target_model.id == AssetAlias.asset_id,
                        AssetAlias.is_primary == True,
                        AssetAlias.status == 1,
                    ),
                    isouter=True,
                )
                .filter(*condition)
                .order_by(target_model.id)
                .paginate(page=page, per_page=page_size, error_out=False)
            )
            
            # 使用AssetListQuerySchema序列化数据
            schema = AssetListQuerySchema()
            dump_data = schema.dump(result.items, many=True)
            return R.paginate(
                data=dump_data,
                total=result.total,
                page=page,
                size=page_size,
                msg="查询成功",
            )
            
        except Exception as e:
            error(f"查询资产列表失败: {str(e)}", exc_info=True)
            return R.fail(msg=f"查询资产列表失败: {str(e)}")

    @api_ns.doc("delete_assets")
    @api_ns.expect(asset_delete_model)
    @api_ns.marshal_with(asset_delete_response_model)
    def delete(self):
        """
        批量删除资产

        删除指定的资产及其关联的分类数据。

        请求参数:
        - ids (list, required): 要删除的资产ID列表

        返回数据格式:
        - 成功响应: {"code": 20000, "data": true, "message": "删除成功", "success": true}
        - 失败响应: {"code": 20500, "data": false, "message": "删除失败: 错误信息", "success": false}

        关键注意事项:
        - 删除操作会同时删除资产数据和相关的分类关联数据
        - 操作失败时会自动回滚事务，确保数据一致性
        - 资产ID必须存在，否则删除操作可能不会产生任何效果

        请求示例:
        DELETE /api/asset/list
        {
            "ids": [1, 2, 3]
        }

        返回示例:
        {
            "code": 20000,
            "data": true,
            "message": "删除成功",
            "success": true
        }
        """
        try:
            data = api.payload
            ids = data.get("ids", [])

            if not ids:
                return R.fail(msg="请提供要删除的资产ID列表")

            # 删除资产数据
            Asset.query.filter(Asset.id.in_(ids)).delete(synchronize_session=False)
            # 删除资产分类关联数据
            AssetCategory.query.filter(AssetCategory.asset_id.in_(ids)).delete(
                synchronize_session=False
            )
            db.session.commit()

            debug(f"成功删除资产，ID列表: {ids}")
            return R.ok(data=True, msg="删除成功")
        except Exception as e:
            db.session.rollback()
            error(f"删除资产失败: {str(e)}", exc_info=True)
            return R.fail(msg=f"删除失败: {str(e)}")


class AssetListSchema(Schema):
    id = fields.Integer()
    asset_name = fields.String(data_key="assetName")
    currency = fields.Integer()
    asset_type = fields.Integer(data_key="assetType")
    category_name = fields.String(data_key="categoryName")
    category_id = fields.Integer(data_key="categoryId")
    f_date = fields.DateTime(data_key="date", format="%Y-%m-%d")
    f_close = fields.String(data_key="close")
    f_close_percent = fields.String(data_key="closePercent")
    code_index = fields.String(data_key="codeIndex")
    code_ttjj = fields.String(data_key="codeTTJJ")
    code_xq = fields.String(data_key="codeXQ")

    @post_dump
    def post_dump(self, data: dict, **kwargs):
        # 字段判断应该使用data_key
        if "close" in data and data["close"] is not None:
            data["close"] = str(Decimal(data["close"]) / 10000)
        if "closePercent" in data and data["closePercent"] is not None:
            data["closePercent"] = str(Decimal(data["closePercent"]) / 10000)
        return data


@api_ns.route("/select")
class AssetSelectRouters(Resource):
    @api_ns.doc("select_assets_by_name")
    def get(self):
        """
        资产选择器查询接口

        根据资产名称进行模糊查询，分页返回资产的 id 与资产名称。

        请求参数：
        - page (int, required): 页码，从1开始
        - pageSize (int, required): 每页条数，建议范围1-100
        - assetName (string, required): 资产名称，支持模糊匹配

        返回数据格式：
        - 成功响应格式：{"code": 20000, "data": {"items": [{"id": 1, "assetName": "招商银行"}], "total": 100, "page": 1, "size": 20}, "message": "查询成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        数据格式说明：
        - 仅返回必要字段 `id/assetName`

        关键注意事项：
        - 仅返回必要字段，支持高频下拉查询场景
        - 使用资产名称模糊匹配

        请求示例：
        GET /api/asset/list/select?page=1&pageSize=20&assetName=招商

        返回示例：
        {
            "code": 20000,
            "data": {
                "items": [
                    {"id": 1, "assetName": "招商银行"}
                ],
                "total": 1,
                "page": 1,
                "size": 20
            },
            "message": "查询成功",
            "success": true
        }
        """
        try:
            raw = request.args.to_dict()
            schema = AssetSelectQuerySchema()
            args = schema.load(raw)
            page = args.get("page")
            page_size = args.get("pageSize")
            asset_name = args.get("assetName")

            conditions = []
            if asset_name:
                conditions.append(Asset.asset_name.like(f"%{asset_name}%"))

            result = (
                db.session.query(Asset.id, Asset.asset_name)
                .filter(*conditions)
                .order_by(Asset.id)
                .paginate(page=page, per_page=page_size, error_out=False)
            )

            items = [
                {"id": row.id, "assetName": row.asset_name}
                for row in result.items
            ]
            return R.paginate(data=items, total=result.total, msg="查询成功")
        except ValidationError as ve:
            return R.fail(msg=f"参数验证失败: {ve.messages}")
        except Exception as e:
            error(f"资产选择器查询失败: {str(e)}", exc_info=True)
            return R.fail(msg=f"查询失败: {str(e)}")
