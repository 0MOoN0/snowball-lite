from flask import request
from flask_restx import Namespace, Resource
from sqlalchemy import func, and_

from web.common.utils import R
from web.models import db
from web.models.asset.asset import Asset
from web.models.asset.asset_alias import AssetAlias
from web.models.record.record import Record
from web.models.record.trade_reference import TradeReference
from web.routers.record.record_list_schemas import (
    RecordListRequestSchema,
    RecordListItemSchema,
    create_record_list_models,
)
from web.common.api_factory import get_api
from web.weblogger import logger

# Flask-RestX Namespace Setup
record_list_ns = Namespace("record_list", description="交易记录列表管理")

api = get_api()
if api:
    api.add_namespace(record_list_ns, path="/api/record_list")

record_models = create_record_list_models(record_list_ns)


@record_list_ns.route("")
class RecordListRouter(Resource):
    """
    交易记录列表路由
    """

    @record_list_ns.doc(
        "list_records",
        params={
            "page": "页码",
            "pageSize": "每页条数",
            "groupType": "分组类型（如 1-网格），用于筛选特定业务类型的记录",
            "groupId": "业务对象ID，需配合 groupType 使用（筛选特定关联ID）",
            "assetName": "资产名称（模糊查询）",
            "assetAlias": "资产别名（模糊查询）",
            "startDate": "开始时间 (yyyy-MM-dd HH:mm:ss)",
            "endDate": "结束时间 (yyyy-MM-dd HH:mm:ss)",
            "transactionsDirection": "交易方向 (0:卖出, 1:买入)",
        },
    )
    @record_list_ns.marshal_with(record_models["record_list_response_model"])
    def get(self):
        """
        分页查询交易记录列表

        1. 接口说明
        - 分页查询交易记录列表，支持多维度筛选。
        - 默认按交易时间倒序排列。
        - 列表项中包含关联的分组类型摘要（groupTypes）。

        2. 请求参数说明
        - page (int, required): 页码
        - pageSize (int, required): 每页条数
        - groupType (int, optional): 分组类型（如 1-网格），用于筛选特定业务类型的记录
        - groupId (int, optional): 业务对象ID，需配合 groupType 使用（筛选特定关联ID）
        - assetName (str, optional): 资产名称（模糊查询）
        - assetAlias (str, optional): 资产别名（模糊查询）
        - startDate (str, optional): 开始时间 (yyyy-MM-dd HH:mm:ss)
        - endDate (str, optional): 结束时间 (yyyy-MM-dd HH:mm:ss)
        - transactionsDirection (int, optional): 交易方向 (0:卖出, 1:买入)

        3. 返回数据格式
        - success (bool): 是否成功
        - code (int): 响应代码
        - message (str): 响应消息
        - data (object):
            - items (list): 记录列表
                - recordId (int): 记录ID
                - ... (基础字段)
                - groupTypes (list[int]): 关联的分组类型列表
            - total (int): 总记录数
            - page (int): 当前页码
            - size (int): 每页条数

        4. 请求示例
        - GET /api/record_list?page=1&pageSize=10
        - GET /api/record_list?page=1&pageSize=10&groupType=1
        - GET /api/record_list?page=1&pageSize=10&assetName=科技
        - GET /api/record_list?page=1&pageSize=10&assetAlias=AAPL
        """
        args = RecordListRequestSchema().load(request.args.to_dict())
        logger.info(f"查询交易记录列表, 参数: {args}")
        page_size = args["page_size"]
        page = args["page"]
        group_type = args.get("group_type")
        group_id = args.get("group_id")
        asset_name = args.get("asset_name")
        asset_alias = args.get("asset_alias")
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        transactions_direction = args.get("transactions_direction")

        # 基础查询构建
        query = db.session.query(
            Record.id.label("record_id"),
            Record.transactions_fee,
            Record.transactions_share,
            Record.transactions_date,
            Record.asset_id,
            Record.transactions_price,
            Record.transactions_direction,
            Record.transactions_amount,
            Asset.asset_name,
            AssetAlias.provider_symbol.label("primary_alias_code"),
            AssetAlias.provider_name.label("primary_provider_name"),
        ).join(Asset, Asset.id == Record.asset_id, isouter=True)

        # 关联主要别名 (Left Join)
        # 注意：这里我们只关联主要别名 (is_primary=1) 用于显示
        # 如果需要根据别名查询，可能需要另外的处理逻辑或 Join
        query = query.join(
            AssetAlias,
            and_(
                AssetAlias.asset_id == Asset.id,
                AssetAlias.is_primary == 1,
                AssetAlias.status == 1,
            ),
            isouter=True,
        )

        # 1. 筛选条件：分组类型与业务ID
        # 如果指定了 groupType，需要 Join TradeReference
        if group_type is not None:
            query = query.join(TradeReference, TradeReference.record_id == Record.id)
            query = query.filter(TradeReference.group_type == group_type)
            # 如果同时指定了 groupId，增加过滤
            if group_id is not None:
                query = query.filter(TradeReference.group_id == group_id)

        # 2. 筛选条件：资产名称
        if asset_name:
            query = query.filter(Asset.asset_name.like(f"%{asset_name}%"))

        # 2.1 筛选条件：资产别名
        if asset_alias:
            # 如果是别名查询，我们需要检查该资产的所有别名，不仅仅是主要别名
            # 使用 exists 子查询
            alias_exists = (
                db.session.query(AssetAlias)
                .filter(
                    AssetAlias.asset_id == Asset.id,
                    AssetAlias.provider_symbol.like(f"%{asset_alias}%"),
                    AssetAlias.status == 1,
                )
                .exists()
            )

            # 使用 correlate(Asset) 明确告诉 SQLAlchemy 这个子查询与外部的 Asset 表相关联
            query = query.filter(alias_exists.correlate(Asset))

        # 3. 筛选条件：时间范围
        if start_date:
            query = query.filter(Record.transactions_date >= start_date)
        if end_date:
            query = query.filter(Record.transactions_date <= end_date)

        # 4. 筛选条件：交易方向
        if transactions_direction is not None:
            query = query.filter(
                Record.transactions_direction == transactions_direction
            )

        # 执行查询并分页
        # 注意：如果有Join TradeReference，可能会有重复记录（如果一个record有多条相同groupType的ref？通常不会，但为了保险可以distinct）
        # 但TradeReference设计上 record_id + group_type + group_id 是唯一的。
        # 如果只筛选 groupType，一个record可能对应多个不同 group_id 的同 type ref？目前业务逻辑似乎不支持。
        # 无论如何，分页前先 order
        records_pagination = query.order_by(Record.transactions_date.desc()).paginate(
            per_page=page_size, page=page, error_out=False
        )
        records = records_pagination.items
        total = records_pagination.total

        # 5. 聚合 group_types
        # 获取当前页所有 record_ids
        record_ids = [r.record_id for r in records]
        group_types_map = {}

        if record_ids:
            group_types_query = (
                db.session.query(
                    TradeReference.record_id,
                    func.group_concat(TradeReference.group_type).label("group_types"),
                )
                .filter(TradeReference.record_id.in_(record_ids))
                .group_by(TradeReference.record_id)
                .all()
            )

            for item in group_types_query:
                if item.group_types:
                    # group_concat返回逗号分隔的字符串，转换为整数列表并去重
                    types = list(set(int(t) for t in item.group_types.split(",")))
                    group_types_map[item.record_id] = types

        # 6. 组装结果
        result_items = []
        for r in records:
            item_dict = {
                "record_id": r.record_id,
                "transactions_fee": r.transactions_fee,
                "transactions_share": r.transactions_share,
                "transactions_date": r.transactions_date,
                "asset_id": r.asset_id,
                "transactions_price": r.transactions_price,
                "transactions_direction": r.transactions_direction,
                "transactions_amount": r.transactions_amount,
                "asset_name": r.asset_name,
                "primary_alias_code": r.primary_alias_code,
                "primary_provider_name": r.primary_provider_name,
                "group_types": group_types_map.get(r.record_id, []),
            }
            result_items.append(item_dict)

        logger.info(f"查询交易记录列表完成, 找到 {total} 条记录")
        # 序列化并返回结果
        return R.paginate(
            data=RecordListItemSchema().dump(result_items, many=True),
            total=total,
            page=page,
            size=page_size,
            msg="查询成功",
        )
