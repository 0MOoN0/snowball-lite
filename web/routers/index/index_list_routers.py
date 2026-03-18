# -*- coding: UTF-8 -*-
"""
@File    ：index_list_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27 15:30
@Description: 指数列表管理接口 - 使用Flask-RestX实现
"""

from flask_restx import Namespace, Resource

from web.common.api_factory import get_api
from web.common.utils import R
from web.models import db
from web.models.index.index_base import IndexBase, IndexBaseSchema
from web.weblogger import debug, error
from .index_list_schemas import create_index_list_models, create_index_list_query_parser

# 创建并注册namespace
api = get_api()
api_ns = Namespace("index_list", description="指数列表管理接口")
if api:
    api.add_namespace(api_ns, path="/api/index/list")

# 创建模型
index_list_models = create_index_list_models(api_ns)
index_list_response_model = index_list_models["index_list_response_model"]

# 创建查询参数解析器
query_parser = create_index_list_query_parser()


@api_ns.route("/")
class IndexListRouters(Resource):
    """指数列表路由类"""

    @api_ns.doc("get_index_list")
    @api_ns.expect(query_parser)
    @api_ns.marshal_with(index_list_response_model)
    def get(self):
        """
        指数列表查询接口

        根据指数名称、指数类型、市场和状态查询指数列表信息，支持分页查询。
        仅查询IndexBase基础对象，不使用子类继承查询。

        请求参数:
        - page (int, required): 页码，从1开始
        - pageSize (int, required): 每页条数，建议范围1-100
        - indexName (string, optional): 指数名称，支持模糊匹配
        - indexType (int, optional): 指数类型（底层资产类型）：0-5之间的整数值
        - investmentStrategy (int, optional): 投资策略：0-3之间的整数值
        - market (int, optional): 所属市场：0-中国，1-香港，2-美国
        - indexStatus (int, optional): 状态：0-停用，1-启用

        返回数据格式:
        - 成功响应格式：{"code": 20000, "data": {"items": [...], "total": 100, "page": 1, "size": 20}, "message": "查询成功", "success": true}
        - 失败响应格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        数据格式说明:
        - 仅包含IndexBase基础字段信息
        - 时间字段格式为ISO 8601格式（YYYY-MM-DDTHH:MM:SS）
        - 日期字段格式为YYYY-MM-DD
        - 枚举字段使用整数值表示

        关键注意事项:
        - 仅查询IndexBase基础对象，不使用子类继承查询
        - 查询结果按指数ID排序，确保数据一致性
        - 支持多条件组合查询，条件之间为AND关系
        - 分页参数必填，避免一次性查询大量数据

        请求示例:
        GET /api/index/list?page=1&pageSize=20&indexName=上证&indexType=0&market=0&indexStatus=1

        返回示例:
        {
            "code": 20000,
            "data": {
                "items": [
                    {
                        "id": 1,
                        "indexCode": "000001.SH",
                        "indexName": "上证指数",
                        "indexType": 0,
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
                        "discriminator": "index_base",
                        "createTime": "2024-01-01T10:00:00",
                        "updateTime": "2024-01-27T15:30:00"
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
        debug("查询指数列表，开始")

        # 解析查询参数
        args = query_parser.parse_args()
        debug(f"查询指数列表，参数：{args}")

        try:
            page = args.get("page")
            page_size = args.get("page_size")
            condition = []
            
            # 构建查询条件
            if args.get("index_name") is not None:
                condition.append(
                    IndexBase.index_name.like("%" + args.get("index_name") + "%")
                )
            if args.get("index_type") is not None:
                condition.append(IndexBase.index_type == args.get("index_type"))
            if args.get("market") is not None:
                condition.append(IndexBase.market == args.get("market"))
            if args.get("index_status") is not None:
                condition.append(IndexBase.index_status == args.get("index_status"))
            
            # 主查询：仅查询IndexBase基础对象
            result = (
                db.session.query(IndexBase)
                .filter(*condition)
                .order_by(IndexBase.id)
                .paginate(page=page, per_page=page_size, error_out=False)
            )
            
            # 使用IndexBaseSchema序列化数据
            schema = IndexBaseSchema()
            dump_data = schema.dump(result.items, many=True)
            return R.paginate(data=dump_data, total=result.total, page=page, size=page_size, msg="查询成功")
            
        except Exception as e:
            error(f"查询指数列表失败: {str(e)}", exc_info=True)
            return R.fail(msg=f"查询指数列表失败: {str(e)}")