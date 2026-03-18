# -*- coding: UTF-8 -*-
"""
@File    ：index_list_schemas.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27 15:30
@Description: 指数列表接口的Flask-RestX模型定义和参数解析器
"""

from flask_restx import fields, Namespace, reqparse
from web.routers.common.response_schemas import get_pagination_response_model


def create_index_list_query_parser():
    """
    创建指数列表查询参数解析器
    
    Returns:
        RequestParser: 配置好的查询参数解析器
    """
    query_parser = reqparse.RequestParser()
    query_parser.add_argument("page", required=True, type=int, location="args", help="页码")
    query_parser.add_argument(
        "pageSize",
        dest="page_size",
        required=True,
        type=int,
        location="args",
        help="每页条数",
    )
    query_parser.add_argument(
        "indexName",
        dest="index_name",
        required=False,
        type=str,
        location="args",
        help="指数名称",
    )
    query_parser.add_argument(
        "indexType",
        dest="index_type",
        required=False,
        type=int,
        location="args",
        help="指数类型（底层资产类型）",
    )
    query_parser.add_argument(
        "investmentStrategy",
        dest="investment_strategy",
        required=False,
        type=int,
        location="args",
        help="投资策略",
    )
    query_parser.add_argument(
        "market",
        required=False,
        type=int,
        location="args",
        help="所属市场",
    )
    query_parser.add_argument(
        "indexStatus",
        dest="index_status",
        required=False,
        type=int,
        location="args",
        help="状态",
    )
    return query_parser


def create_index_list_models(api_ns):
    """
    创建指数列表相关的Flask-RestX模型
    
    Args:
        api_ns: Flask-RestX Namespace实例
        
    Returns:
        dict: 包含所有模型的字典
    """
    
    # 指数列表项模型
    index_list_item_model = api_ns.model('IndexListItem', {
        'id': fields.Integer(description='指数ID', example=1),
        'indexCode': fields.String(description='指数代码', example='000001.SH'),
        'indexName': fields.String(description='指数名称', example='上证指数'),
        'indexType': fields.Integer(description='指数类型（底层资产类型）：0-股票指数，1-债券指数，2-商品指数，3-货币指数，4-混合指数，5-其他', example=0),
        'investmentStrategy': fields.Integer(description='投资策略：0-宽基指数，1-行业指数，2-主题指数，3-策略指数', example=0),
        'market': fields.Integer(description='所属市场：0-中国，1-香港，2-美国', example=0),
        'baseDate': fields.String(description='基准日期', example='1990-12-19'),
        'basePoint': fields.Integer(description='基准点数', example=100),
        'currency': fields.Integer(description='计价货币：0-人民币，1-美元，2-欧元，3-港币', example=0),
        'weightMethod': fields.Integer(description='权重计算方法：0-市值加权，1-等权重，2-基本面加权，3-其他', example=0),
        'calculationMethod': fields.Integer(description='计算方法：0-价格加权，1-总收益，2-净收益，3-其他', example=1),
        'indexStatus': fields.Integer(description='状态：0-停用，1-启用', example=1),
        'description': fields.String(description='指数描述', example='反映上海证券交易所挂牌股票总体走势的统计指标'),
        'publisher': fields.String(description='发布机构', example='上海证券交易所'),
        'publishDate': fields.String(description='发布日期', example='1991-07-15'),
        'discriminator': fields.String(description='多态标识符', example='index_base'),
        'createTime': fields.String(description='创建时间', example='2024-01-01T10:00:00'),
        'updateTime': fields.String(description='更新时间', example='2024-01-27T15:30:00')
    })
    
    # 指数列表分页响应模型
    index_list_response_model = get_pagination_response_model(index_list_item_model)
    
    return {
        'index_list_item_model': index_list_item_model,
        'index_list_response_model': index_list_response_model
    }