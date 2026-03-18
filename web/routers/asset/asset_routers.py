# -*- coding: UTF-8 -*-
"""
@File    ：asset_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27
@Description: 资产管理接口 - 使用Flask-RestX实现
"""

from flask_restx import Resource
from marshmallow import ValidationError
from sqlalchemy.orm import with_polymorphic

from web.common.api_factory import get_api
from web.models import db
from web.models.asset.asset import Asset, AssetExchangeFund
from web.models.asset.asset_fund import AssetFund, AssetFundETF, AssetFundLOF
from web.services.asset.asset_inheritance_update_service import AssetInheritanceUpdateService
from web.weblogger import logger
from .asset_routers_schemas import create_asset_schemas, AssetUpdateSchema
from ...common.utils import R

# 创建API实例
api = get_api()

# 创建Namespace
api_ns = api.namespace("asset", description="资产相关接口", path="/api/asset")

# 创建模型
schemas = create_asset_schemas(api_ns)
polymorphic_asset_response_model = schemas['polymorphic_asset_response_model']
asset_update_model = schemas['asset_update_model']


@api_ns.route("/<int:asset_id>")
class AssetRouters(Resource):
    @api_ns.marshal_with(polymorphic_asset_response_model)
    @api_ns.doc("get_asset_by_id")
    def get(self, asset_id):
        """
        根据ID获取资产详情
        支持多态返回，根据asset_subtype自动适配对应的数据模型结构
        使用with_polymorphic实现非延迟加载的多态查询

        通过资产ID获取指定资产的详细信息，一次性获取所有子类数据。
        根据不同的资产类型(asset_type)，返回对应的数据结构。

        路径参数:
        - asset_id (int, required): 资产的唯一标识ID

        返回数据格式:
        - 成功响应: {"code": 20000, "data": {...}, "message": "成功", "success": true}
        - 失败响应: {"code": 20500, "data": false, "message": "错误信息", "success": false}

        多态返回数据结构说明:
        根据asset_type的不同，data字段会返回不同的数据结构：

        1. 普通基金 (asset_type=1):
        {
            "id": 123,
            "assetName": "易方达蓝筹精选",
            "assetCode": "005827",
            "assetShortCode": "YFDLCJX",
            "assetType": 1,
            "assetStatus": 0,
            "currency": 0,
            "market": 0,
            "fundType": "STOCK_FUND",
            "tradingMode": "OPEN_END",
            "fundCompany": "易方达基金管理有限公司",
            "fundManager": "张坤",
            "establishmentDate": "2018-03-01",
            "fundScale": 15000.0000,
            "fundStatus": 0,
            "investmentObjective": "追求长期资本增值",
            "investmentStrategy": "价值投资策略"
        }

        2. 股票 (asset_type=2):
        {
            "id": 123,
            "assetName": "中国平安",
            "assetCode": "601318",
            "assetShortCode": "ZGPA",
            "assetType": 2,
            "assetStatus": 0,
            "currency": 0,
            "market": 0
        }

        3. 基础资产 (asset_type=3):
        {
            "id": 123,
            "assetName": "基础资产名称",
            "assetCode": "CODE001",
            "assetShortCode": "BASE001",
            "assetType": 3,
            "assetStatus": 0,
            "currency": 0,
            "market": 0
        }

        4. ETF基金 (asset_type=4):
        {
            "id": 123,
            "assetName": "华夏上证50ETF",
            "assetCode": "510050",
            "assetShortCode": "50ETF",
            "assetType": 4,
            "assetStatus": 0,
            "currency": 0,
            "market": 0,
            "fundType": "INDEX_FUND",
            "tradingMode": "ETF",
            "fundCompany": "华夏基金管理有限公司",
            "fundManager": "张弘弢",
            "establishmentDate": "2004-12-30",
            "fundScale": 50000.0000,
            "fundStatus": 0,
            "investmentObjective": "跟踪上证50指数",
            "investmentStrategy": "被动指数投资策略",
            "trackingIndexCode": "000016",
            "trackingIndexName": "上证50指数",
            "indexId": 1,
            "primaryExchange": "上海证券交易所",
            "dividendFrequency": "年度",
            "trackingError": 0.05
        }

        5. LOF基金 (asset_type=5):
        {
            "id": 123,
            "assetName": "华夏回报混合LOF",
            "assetCode": "002001",
            "assetShortCode": "HXHB",
            "assetType": 5,
            "assetStatus": 0,
            "currency": 0,
            "market": 0,
            "fundType": "HYBRID_FUND",
            "tradingMode": "LOF",
            "fundCompany": "华夏基金管理有限公司",
            "fundManager": "蔡向阳",
            "establishmentDate": "2003-09-05",
            "fundScale": 8000.0000,
            "fundStatus": 0,
            "investmentObjective": "追求稳健收益",
            "investmentStrategy": "混合投资策略",
            "listingExchange": "深圳证券交易所",
            "subscriptionFeeRate": 1.5,
            "redemptionFeeRate": 0.5,
            "navCalculationTime": "15:00",
            "tradingSuspensionInfo": "正常交易",
            "indexId": null
        }

        请求示例:
        - GET /api/asset/123

        关键注意事项:
        - 资产ID必须存在，否则返回失败响应
        - 返回的数据结构根据asset_type动态变化
        - 所有子类型都包含基础字段(id, assetName, assetCode, assetShortCode, assetType, assetStatus, currency, market, createTime, updateTime)
        - 基金类型(asset_type=1,4,5)会额外包含基金特有字段(fundType, tradingMode, fundCompany等)
        - ETF基金(asset_type=4)额外包含ETF特有字段(trackingIndexCode, trackingIndexName等)
        - LOF基金(asset_type=5)额外包含LOF特有字段(listingExchange, subscriptionFeeRate等)
        - 时间字段格式为 ISO 8601 格式 (YYYY-MM-DDTHH:MM:SS)
        - 日期字段格式为 YYYY-MM-DD
        - 枚举字段使用整数值：assetType(1=基金,2=股票,3=基础资产,4=ETF基金,5=LOF基金)
        - 状态字段使用整数值：assetStatus(0=活跃,1=退市), currency(0=人民币,1=美元等), market(0=中国,1=香港,2=美国)
        """
        try:
            logger.info(f"获取资产详情，资产ID: {asset_id}")

            # 使用with_polymorphic进行多态查询，一次性获取所有子类数据
            # 创建多态查询对象，包含所有子类
            poly_asset = with_polymorphic(Asset, [AssetExchangeFund, AssetFund, AssetFundETF, AssetFundLOF])
            
            # 执行多态查询，自动返回正确的子类实例
            asset = db.session.query(poly_asset).filter(poly_asset.id == asset_id).first()
            
            if not asset:
                logger.warning(f"资产不存在，资产ID: {asset_id}")
                return R.fail(msg=f"资产不存在，ID: {asset_id}")

            # 获取资产子类型
            asset_subtype = asset.asset_subtype
            
            # 使用动态序列化函数根据子类型序列化数据
            result = asset.serialize_to_vo(asset_subtype)
            
            # 为 fields.Polymorph 添加判别字段
            # Flask-RESTX 的 marshal_with 会根据 assetSubtype 字段选择对应的模型进行序列化
            result['assetSubtype'] = asset_subtype

            logger.info(f"成功获取资产详情，资产ID: {asset_id}, 子类型: {asset_subtype}")
            return R.ok(data=result, msg="获取资产详情成功")

        except Exception as e:
            logger.error(f"获取资产详情失败，资产ID: {asset_id}, 错误: {str(e)}", exc_info=True)
            return R.fail(msg=f"获取资产详情失败: {str(e)}")

    @api_ns.expect(asset_update_model, validate=False)  # 关闭 Flask-RestX 验证，仅用于文档展示
    @api_ns.marshal_with(polymorphic_asset_response_model)
    @api_ns.doc("update_asset_by_id")
    def put(self, asset_id):
        """
        根据ID更新资产详情
        支持多态更新，通过传入的assetType自动推导资产子类型。
        如果资产类型发生变更，将自动切换到对应的子类型。

        路径参数:
        - asset_id (int, required): 资产的唯一标识ID

        请求体 (JSON):
        基础资产字段（Asset模型）:
        - assetName (string, required): 资产名称，不能为空
        - assetCode (string, optional): 资产代码，可为空
        - assetShortCode (string, optional): 资产简短代码，可为空
        - assetType (integer, required): 资产类型，不能为空 (1=基金,2=股票,3=基础资产,4=ETF基金,5=LOF基金)
        - assetStatus (integer, required): 资产状态，不能为空 (0=活跃,1=退市)
        - market (integer, optional): 所在市场，可为空 (0=中国,1=香港,2=美国)
        - currency (integer, optional): 货币类型，可为空 (0=人民币,1=美元)
        
        基金资产字段（AssetFund模型，当assetType为1,4,5时适用）:
        - fundType (string, required): 基金投资策略类型，不能为空
        - tradingMode (string, required): 基金交易方式，不能为空
        - fundStatus (integer, required): 基金状态，不能为空 (0=正常运作,1=暂停申购/赎回,2=已清盘,3=已合并)
        - fundCompany (string, optional): 基金管理公司名称，可为空
        - fundManager (string, optional): 基金经理姓名，可为空
        - establishmentDate (date, optional): 基金成立日期，可为空 (格式: YYYY-MM-DD)
        - fundScale (float, optional): 基金规模（万元），可为空
        - investmentObjective (string, optional): 投资目标描述，可为空
        - investmentStrategy (string, optional): 投资策略描述，可为空
        
        ETF基金特有字段（AssetFundETF模型，当assetType为4时适用）:
        - trackingIndexCode (string, optional): 跟踪指数代码，可为空
        - trackingIndexName (string, optional): 跟踪指数名称，可为空
        - indexId (integer, optional): 关联的指数ID，可为空
        - primaryExchange (string, optional): 主要交易所，可为空
        - dividendFrequency (string, optional): 分红频率，可为空
        - trackingError (float, optional): 跟踪误差，可为空
        
        LOF基金特有字段（AssetFundLOF模型，当assetType为5时适用）:
        - listingExchange (string, optional): 上市交易所，可为空
        - subscriptionFeeRate (float, optional): 申购费率，可为空
        - redemptionFeeRate (float, optional): 赎回费率，可为空
        - navCalculationTime (string, optional): 净值计算时间，可为空
        - tradingSuspensionInfo (string, optional): 停牌信息，可为空

        返回数据格式:
        - 成功响应: {"code": 20000, "data": {...}, "message": "成功", "success": true}
        - 失败响应: {"code": 20500, "data": false, "message": "错误信息", "success": false}

        请求示例:
        - PUT /api/asset/123
        - Body (更新基础资产): 
        {
            "assetName": "中国平安",
            "assetType": 2,
            "assetStatus": 0,
            "assetCode": "601318",
            "market": 0,
            "currency": 0
        }
        
        - Body (更新基金资产):
        {
            "assetName": "易方达蓝筹精选混合A",
            "assetType": 1,
            "assetStatus": 0,
            "fundType": "HYBRID_FUND",
            "tradingMode": "OPEN_END",
            "fundStatus": 0,
            "fundCompany": "易方达基金管理有限公司",
            "fundManager": "张坤",
            "fundScale": 15000.0
        }

        返回示例:
        - 成功响应:
        {
            "code": 20000,
            "success": true,
            "message": "资产更新成功",
            "data": {
                "id": 123,
                "assetName": "中国平安",
                "assetCode": "601318",
                "assetType": 2,
                "assetStatus": 0,
                "market": 0,
                "currency": 0,
                "createTime": "2024-01-01T10:00:00",
                "updateTime": "2024-01-27T15:30:00"
            }
        }
        
        - 失败响应:
        {
            "code": 20500,
            "success": false,
            "message": "资产不存在，ID: 999",
            "data": false
        }

        关键注意事项:
        - 资产ID必须存在，否则返回失败响应
        - 必填字段不能为空：assetName、assetType、assetStatus
        - 基金类型资产的必填字段：fundType、tradingMode、fundStatus
        - 系统根据assetType自动推导asset_subtype，无需客户端传入
        - 切换资产类型是破坏性操作，会清除原类型特有数据
        - 更新时提供的字段会覆盖旧值，未提供的字段保持不变
        - 字段名使用驼峰命名法，与数据库字段的下划线命名自动转换
        - 日期字段格式为 YYYY-MM-DD，时间字段格式为 ISO 8601 格式
        - 枚举字段使用整数值，具体含义见字段说明
        """
        try:
            logger.info(f"开始更新资产，ID: {asset_id}")
            data = api.payload

            if not data:
                logger.warning(f"更新数据为空，ID: {asset_id}")
                return R.fail(msg="更新数据不能为空")

            # 使用 Marshmallow Schema 进行数据验证和转换
            schema = AssetUpdateSchema()
            try:
                # 验证并转换数据（包括驼峰命名到下划线命名的转换）
                validated_data = schema.load(data)
                logger.info(f"Marshmallow 验证成功，转换后的数据: {validated_data}")
                
            except ValidationError as ve:
                # 直接将验证错误信息拼接到msg中
                logger.warning(f"数据验证失败，ID: {asset_id}, 错误: {ve.messages}")
                return R.fail(msg=f"数据验证失败: {ve.messages}", data=ve.messages)

            # 使用AssetInheritanceUpdateService处理多态转换更新
            # 注意：这里传入验证后的数据，已经是下划线命名格式
            inheritance_service = AssetInheritanceUpdateService()
            success, message = inheritance_service.update_with_polymorphic_conversion(asset_id, validated_data)
            
            if success:
                # 重新查询更新后的数据以返回给客户端
                poly_asset = with_polymorphic(Asset, "*")
                updated_asset = db.session.query(poly_asset).filter(Asset.id == asset_id).first()
                
                if updated_asset:
                    # 使用Asset的serialize_to_vo方法进行序列化
                    result = updated_asset.serialize_to_vo()
                    # 添加assetSubtype字段用于前端识别
                    result['assetSubtype'] = updated_asset.asset_subtype
                    logger.info(f"资产更新成功，ID: {asset_id}, 子类型: {updated_asset.asset_subtype}")
                    return R.ok(data=result, msg=message)
                else:
                    logger.error(f"更新后无法查询到资产，ID: {asset_id}")
                    return R.fail(msg="更新后无法查询到资产")
            else:
                return R.fail(msg=message)

        except Exception as e:
            logger.error(f"更新资产详情失败，ID: {asset_id}, 错误: {str(e)}", exc_info=True)
            return R.fail(msg=f"更新资产详情失败: {str(e)}")