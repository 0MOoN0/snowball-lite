# -*- coding: UTF-8 -*-
"""
@File    ：index_detail_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27 16:00
@Description: 指数详情管理接口 - 使用Flask-RestX实现单个指数的CRUD操作
"""

from flask_restx import Namespace, Resource, reqparse
from marshmallow import ValidationError

from web.common.api_factory import get_api
from web.common.utils import R
from web.models import db
from web.models.index.index_base import IndexBase
from web.models.index.index_stock import StockIndex
from web.weblogger import debug, error
from .index_detail_schemas import create_index_create_models
from web.routers.common.response_schemas import get_base_response_model
from sqlalchemy.orm import with_polymorphic
from .index_detail_schemas import create_index_update_models, IndexUpdateSchema
from web.services.index.index_inheritance_update_service import IndexInheritanceUpdateService
from sqlalchemy.orm import selectinload

# 创建并注册namespace
api = get_api()
api_ns = Namespace("index_detail", description="指数详情管理接口")
if api:
    api.add_namespace(api_ns, path="/api/index")

# 创建模型
models = create_index_create_models(api_ns)
index_create_model = models['index_create_model']
base_response_model = get_base_response_model()

# 创建更新模型
update_models = create_index_update_models(api_ns)
index_update_model = update_models['index_update_model']

# 详情查询参数解析器（用于集合资源 GET）
detail_query_parser = reqparse.RequestParser()
detail_query_parser.add_argument('id', required=False, type=int, location='args', help='指数ID')
detail_query_parser.add_argument('indexCode', dest='index_code', required=False, type=str, location='args', help='指数代码')

@api_ns.route("/")
class IndexCollection(Resource):
    """指数集合资源：仅负责创建（POST）"""

    @api_ns.doc("create_index")
    @api_ns.expect(index_create_model, validate=False)
    @api_ns.marshal_with(base_response_model, description="创建成功")
    def post(self):
        """
        指数新增接口

        创建新的指数数据，支持基础指数和股票指数两种类型。
        根据 indexType 字段自动判断创建的指数类型。
         
         请求体参数:
         - indexCode (string, required): 指数代码，如000001.SH，必须唯一
         - indexName (string, required): 指数名称，不能为空
         - indexType (integer, required): 指数类型（底层资产类型），0-5之间的整数值
         - investmentStrategy (integer, optional): 投资策略，0-3之间的整数值
         - market (integer, required): 所属市场，0-中国，1-香港，2-美国

         - baseDate (string, optional): 基准日期，格式：YYYY-MM-DD
         - basePoint (integer, optional): 基准点数
         - currency (integer, optional): 计价货币，0-人民币，1-美元，2-欧元，3-港币
         - weightMethod (integer, optional): 权重计算方法，0-市值加权，1-等权重，2-基本面加权，3-其他
         - calculationMethod (integer, optional): 计算方法，0-价格加权，1-总收益，2-净收益，3-其他
         - indexStatus (integer, optional): 状态，0-停用，1-启用，默认为1
         - description (string, optional): 指数描述
         - publisher (string, optional): 发布机构
         - publishDate (string, optional): 发布日期，格式：YYYY-MM-DD

        股票指数特有字段（当 indexType 对应股票指数时）:

         - constituentCount (integer, optional): 成分股数量
         - marketCap (float, optional): 总市值（万元）
         - freeFloatMarketCap (float, optional): 自由流通市值（万元）
         - averagePe (float, optional): 平均市盈率
         - averagePb (float, optional): 平均市净率
         - dividendYield (float, optional): 股息率（%）
         - turnoverRate (float, optional): 换手率（%）
         - volatility (float, optional): 波动率（%）
         - beta (float, optional): 贝塔系数
         - rebalanceFrequency (string, optional): 调仓频率，quarterly-季度，semi_annual-半年，annual-年度
         - lastRebalanceDate (string, optional): 最后调仓日期，格式：YYYY-MM-DD
         - nextRebalanceDate (string, optional): 下次调仓日期，格式：YYYY-MM-DD
 
         返回数据格式:
         - 成功响应: {"code": 20000, "data": {...}, "message": "指数创建成功", "success": true}
         - 失败响应: {"code": 20500, "data": false, "message": "错误信息", "success": false}
 
         关键注意事项:
         - 指数代码（indexCode）必须唯一，重复时返回失败响应
         - 必填字段不能为空：indexCode、indexName、indexType、market
        - 根据 indexType 字段自动选择创建基础指数或股票指数
         - 创建成功后返回包含ID和时间戳的完整指数信息
         - 数据验证失败时返回详细的错误信息
 
         请求示例:
         POST /api/index/
         {
             "indexCode": "000001.SH",
             "indexName": "上证综指",
             "indexType": 0,
             "market": 0,

             "baseDate": "1990-12-19",
             "basePoint": 100,
             "indexStatus": 1,
             "description": "反映上海证券交易所挂牌股票总体走势的统计指标",
             "publisher": "上海证券交易所"
         }
 
         返回示例:
         成功响应:
         {
             "code": 20000,
             "success": true,
             "message": "指数创建成功",
             "data": {
                 "id": 123,
                 "indexCode": "000001.SH",
                 "indexName": "上证综指",

                 "createTime": "2024-01-27T15:30:00",
                 "updateTime": "2024-01-27T15:30:00"
             }
         }

        失败响应:
        {
            "code": 20500,
            "success": false,
            "message": "指数代码 '000001.SH' 已存在",
            "data": false
        }
        """
        debug("新增指数，开始")

        try:
            # 使用 api.payload 获取请求数据（驼峰）
            json_data = api_ns.payload
            debug(f"新增指数，参数：{json_data}")

            # 仅用 indexType 决定子类，discriminator 内部使用
            index_type = json_data.get('indexType')
            if index_type is None:
                return R.fail(msg="indexType 不能为空")
            
            # 后端根据 indexType 决定内部 discriminator，不对外暴露
            subtype = IndexBase.get_subtype_by_type(index_type)
            # 选择创建Schema（模型侧方法提供），一次校验一次反序列化
            create_schema = IndexBase.get_create_schema_for_type(index_type)
            try:
                new_index = create_schema.load(json_data)
            except ValidationError as ve:
                debug(f"数据校验失败：{ve.messages}")
                return R.fail(msg=f"数据校验失败：{ve.messages}")
 
            # 内部设置 discriminator，避免外部传入
            try:
                new_index.discriminator = subtype
            except Exception:
                # 若模型映射未包含该字段，忽略设置
                pass

            # 检查指数代码是否已存在
            existing_index = IndexBase.query.filter_by(index_code=new_index.index_code).first()
            if existing_index:
                return R.fail(msg=f"指数代码 '{new_index.index_code}' 已存在")

            # 保存到数据库
            db.session.add(new_index)
            db.session.commit()

            debug(f"新增指数成功，ID：{new_index.id}")

            # 使用serialize_to_vo方法序列化返回数据
            result_data = new_index.serialize_to_vo()

            return R.ok(data=result_data, msg="指数创建成功")

        except Exception as e:
            db.session.rollback()
            error(f"新增指数失败：{str(e)}", exc_info=True)
            return R.fail(msg=f"创建指数失败：{str(e)}")

    @api_ns.doc("get_index_detail")
    @api_ns.expect(detail_query_parser)
    @api_ns.marshal_with(base_response_model, description="查询成功")
    def get(self):
        """
        指数详情查询接口

        仅支持按 `id` 或 `indexCode` 查询单个指数的详细信息。
        使用 with_polymorphic 一次性加载子类字段，返回的数据会根据指数类型包含相应字段，且不返回内部字段 `discriminator`。
        
        路径参数说明（必填）：
        - 无（本接口使用查询参数）
        
        查询参数说明（必填）：
        - id (int, optional): 指数ID，主键；当同时提供id与indexCode时，优先使用id
        - indexCode (string, optional): 指数代码，如 000001.SH；至少与id之一提供
        
        返回数据格式（必填）：
        - 成功响应：{"code": 20000, "data": {...}, "message": "查询成功", "success": true}
        - 失败响应：{"code": 20500, "data": false, "message": "错误信息", "success": false}
        
        
        关键注意事项（必填）：
        - `id` 与 `indexCode` 至少提供一个；仅作为详情查询，不支持组合筛选
        
        请求示例（必填）：
        - GET /api/index/?id=123
        - GET /api/index/?indexCode=000001.SH
        
        返回示例（必填）：
        成功响应（基础指数）：
        {
            "code": 20000,
            "success": true,
            "message": "查询成功",
            "data": {
                "id": 123,
                "indexCode": "000001.SH",
                "indexName": "上证综指",
                "indexType": 0,
                "investmentStrategy": 0,
                "market": 0,
                "baseDate": "1990-12-19",
                "basePoint": 100,
                "currency": 0,
                "weightMethod": 0,
                "calculationMethod": 1,
                "indexStatus": 1,
                "description": "反映上海证券交易所挂牌股票总体走势的统计指标",
                "publisher": "上海证券交易所",
                "publishDate": "1991-07-15",
                "createTime": "2024-01-01T10:00:00",
                "updateTime": "2024-01-27T15:30:00"
            }
        }
        
        失败响应：
        {
            "code": 20500,
            "success": false,
            "message": "未找到对应指数",
            "data": false
        }
        """
        debug("查询指数详情，开始")
        try:
            args = detail_query_parser.parse_args()
            debug(f"查询指数详情，参数：{args}")

            index_id = args.get('id')
            index_code = args.get('index_code')

            # 使用with_polymorphic进行多态查询，确保一次性加载子类字段
            poly_index = with_polymorphic(IndexBase, [StockIndex])

            # 必须提供 id 或 indexCode
            if index_id is None and (index_code is None or len(index_code.strip()) == 0):
                return R.fail(msg="id 或 indexCode 必须提供其一")

            # 优先使用ID查询
            index_obj = None
            if index_id is not None:
                index_obj = db.session.query(poly_index).filter(poly_index.id == index_id).first()
            else:
                index_obj = db.session.query(poly_index).filter(poly_index.index_code == index_code).first()

            if index_obj is None:
                return R.fail(msg="未找到对应指数")

            # 根据多态标识序列化（内部自动选择VO Schema），不返回discriminator
            result_data = index_obj.serialize_to_vo()

            return R.ok(data=result_data, msg="查询成功")
        except Exception as e:
            error(f"查询指数详情失败：{str(e)}", exc_info=True)
            return R.fail(msg=f"查询失败：{str(e)}")
@api_ns.route("/<int:index_id>")
class IndexItem(Resource):
    """指数单项资源：负责更新（PUT）、删除（DELETE）"""

    @api_ns.doc("update_index_detail")
    @api_ns.expect(index_update_model, validate=False)
    @api_ns.marshal_with(base_response_model, description="更新成功")
    def put(self, index_id: int = None):
        """
        指数详情更新接口（仅返回操作结果）

        根据路径参数 `index_id` 更新单个指数的详情，支持继承的多态转换：当 `indexType` 发生变化时，系统会将当前实例转换为对应的子类（如基础指数 IndexBase → 股票指数 StockIndex）。未提供的字段保持原值，提供的字段会覆盖旧值。

        路径参数说明
        - index_id (int, required): 指数唯一ID，用于定位待更新的记录

        返回数据格式
        - 成功响应：`{"code": 20000, "data": true, "message": "更新成功", "success": true}`
        - 失败响应：`{"code": 20500, "data": false, "message": "错误信息", "success": false}`

        数据格式说明
        - 本接口不再返回更新后的详细数据，仅返回操作结果布尔值。前端若需最新详情，请调用 GET `/api/index/?id=...` 查询。
        - 请求体采用驼峰命名；后端自动进行驼峰→下划线转换与类型校验。

        关键注意事项
        - `index_id` 必须通过路径提供；请求体不可为空。
        - 多态转换规则：当 `indexType` 由非股票（如 5-OTHER）变更为 0-STOCK 时，会自动创建股票指数子类并迁移字段；反向亦然。
        - 未提供的字段不修改；仅对出现于请求体的字段进行覆盖更新。
        - 响应仅表示操作是否成功，不包含更新后的对象数据。

        请求示例
        - PUT `/api/index/123`
        Body（基础指数字段更新，不改变类型）：
        {
          "indexName": "更新后-基础指数",
          "indexType": 5,
          "indexStatus": 1,
          "market": 0
        }
        - PUT `/api/index/123`
        Body（多态转换为股票指数）：
        {
          "indexName": "转换后-股票指数",
          "indexType": 0,
          "indexStatus": 1,
          "market": 0,
          "constituentCount": 30,
          "averagePe": 11.1,
          "rebalanceFrequency": "quarterly"
        }

        返回示例（必填）
        - 成功：
        {
          "code": 20000,
          "success": true,
          "message": "更新成功",
          "data": true
        }
        - 失败（参数校验失败）：
        {
          "code": 20500,
          "success": false,
          "message": "数据验证失败：{...}",
          "data": false
        }
        """
        if index_id is None:
            return R.fail(msg="index_id 必须通过路径提供")
        debug(f"开始更新指数，ID: {index_id}")
        try:
            data = api_ns.payload
            if not data:
                return R.fail(msg="更新数据不能为空")

            schema = IndexUpdateSchema()
            try:
                validated_data = schema.load(data)
                debug(f"Marshmallow 验证成功，转换后的数据: {validated_data}")
            except ValidationError as ve:
                debug(f"数据验证失败，ID: {index_id}, 错误: {ve.messages}")
                return R.fail(msg=f"数据验证失败：{ve.messages}", data=ve.messages)

            service = IndexInheritanceUpdateService()
            success, message = service.update_with_polymorphic_conversion(index_id, validated_data)

            if success:
                # 仅返回操作结果，不再查询更新后的值
                debug(f"指数更新成功，ID: {index_id}")
                return R.ok(data=True, msg=message)
            else:
                return R.fail(msg=message)

        except Exception as e:
            db.session.rollback()
            error(f"更新指数详情失败，ID: {index_id}, 错误: {str(e)}", exc_info=True)
            return R.fail(msg=f"更新指数详情失败：{str(e)}")

    @api_ns.doc("delete_index_detail")
    @api_ns.marshal_with(base_response_model, description="删除成功")
    def delete(self, index_id: int = None):
        """
        指数删除接口（ORM级联删除）

        根据路径参数 `index_id` 删除单个指数。使用 ORM 实例删除方式自动处理继承链（IndexBase ↔ StockIndex）和别名集合（IndexAlias，依赖模型的 cascade 配置）。该操作不可恢复，请谨慎使用。

        路径参数说明（必填）
        - index_id (int, required): 指数唯一ID

        返回数据格式（必填）
        - 成功响应：{"code": 20000, "data": true, "message": "删除成功", "success": true}
        - 失败响应：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        关键注意事项（必填）
        - 操作不可逆，删除后无法恢复
        - 通过 ORM 级联配置（cascade='all, delete-orphan'）删除别名集合；继承链由 ORM 自动生成多表删除语句
        - 本接口仅返回操作结果，若需确认请再次调用 GET `/api/index/?id=...`

        请求示例（必填）
        - DELETE `/api/index/123`

        返回示例（必填）
        - 成功：{"code": 20000, "success": true, "message": "删除成功", "data": true}
        - 失败：{"code": 20500, "success": false, "message": "未找到对应指数", "data": false}
        """
        if index_id is None:
            return R.fail(msg="index_id 必须通过路径提供")
        debug(f"开始删除指数，ID: {index_id}")
        try:
            # 先确认存在，并预加载别名集合以触发 ORM 级联删除
            base_obj = db.session.query(IndexBase).options(selectinload(IndexBase.aliases)).filter(IndexBase.id == index_id).first()
            if base_obj is None:
                return R.fail(msg="未找到对应指数")

            # ORM 实例删除：自动处理继承子表与已加载的关联集合
            db.session.delete(base_obj)
            db.session.commit()

            debug(f"删除指数成功，ID: {index_id}")
            return R.ok(data=True, msg="删除成功")
        except Exception as e:
            db.session.rollback()
            error(f"删除指数失败，ID: {index_id}, 错误: {str(e)}", exc_info=True)
            return R.fail(msg=f"删除失败：{str(e)}")