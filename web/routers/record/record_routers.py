import pandas as pd
from flask import Blueprint
from flask_restful import Api, Resource as RestfulResource, reqparse
from flask_restx import Namespace, Resource
from pandas import DataFrame
from sqlalchemy import and_
from werkzeug.datastructures import FileStorage

import web.common.enum.webEnum
from web.common.api_factory import get_api
from web.models.asset.asset import Asset
from web.web_exception import WebBaseException
from web.common.cons import webcons
from web.common.enum.StrategyEnum import StrategyEnum
from web.common.utils import R
from web.models import db
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.record.record import RecordSchema, Record
from web.models.record.trade_reference import TradeReference
from web.routers.record.record_schemas import (
    create_record_models,
    RecordUpdateSchema,
    RecordCreateSchema,
)
from web.weblogger import debug, logger
from web.common.enum.business.record.trade_reference_enum import (
    TradeReferenceGroupTypeEnum,
)


record_file_bp = Blueprint("record_file", __name__, url_prefix="/record_file")
record_file_api = Api(record_file_bp)


# Flask-RestX Namespace Setup
record_ns = Namespace("record", description="交易记录管理")

api = get_api()
if api:
    api.add_namespace(record_ns, path="/api/record")

record_models = create_record_models(record_ns)


@record_ns.route("")
class RecordCollectionRouters(Resource):
    @record_ns.doc("create_record")
    @record_ns.expect(record_models["record_create_model"], validate=False)
    @record_ns.marshal_with(record_models["record_response_model"])
    def post(self):
        """
        新增交易记录

        1. 接口说明
        - 新增一条交易记录。
        - 支持同时创建一条初始业务关联（通过 groupType 和 groupId）。

        2. 请求参数说明
        - assetId (int, required): 资产ID
        - transactionsShare (int, required): 交易份额
        - transactionsPrice (int, required): 交易价格（单位：厘）
        - transactionsFee (int, required): 交易费用（单位：厘）
        - transactionsDirection (int, required): 交易方向 (0:卖出, 1:买入)
        - transactionsDate (str, required): 交易时间 (yyyy-MM-dd HH:mm:ss)
        - groupType (int, optional): 关联分组类型（如 1-网格）
        - groupId (int, optional): 关联业务对象ID

        3. 自动计算与校验
        - transactionsAmount: 如果未提供，自动根据 share * price 计算。
        - 关联校验: 如果 groupType=1 (网格)，会校验 groupId 对应的网格类型是否存在。

        4. 返回数据格式
        - success (bool): 是否成功
        - message (str): 结果消息

        5. 请求示例
        {
            "assetId": 101,
            "transactionsShare": 100,
            "transactionsPrice": 10000,
            "transactionsFee": 5,
            "transactionsDirection": 1,
            "transactionsDate": "2023-10-27 10:00:00",
            "groupType": 1,
            "groupId": 1
        }
        """
        data = RecordCreateSchema().load(record_ns.payload)
        logger.info(f"新增交易记录, 参数: {data}")

        # Calculate transactions_amount if not provided or recalculate
        if "transactions_amount" not in data or data["transactions_amount"] is None:
            share = data.get("transactions_share", 0)
            price = data.get("transactions_price", 0)
            data["transactions_amount"] = share * price

        # 提取关联信息
        group_type = data.pop("group_type", 0)
        group_id = data.pop("group_id", None)

        # Create Record object
        record = Record(**data)

        # 验证资产是否存在
        asset = db.session.get(Asset, data.get("asset_id"))
        if not asset:
            return R.fail(msg="资产不存在")

        try:
            # 使用事务处理
            db.session.add(record)
            db.session.flush()

            # 如果提供了group_id，添加交易关联记录
            if group_id is not None:
                # 校验GridType
                if group_type == TradeReferenceGroupTypeEnum.GRID.value:
                    grid_type = db.session.get(GridType, group_id)
                    if not grid_type:
                        db.session.rollback()
                        return R.fail(msg="网格类型不存在")

                trade_reference = TradeReference(
                    record_id=record.id, group_type=group_type, group_id=group_id
                )
                db.session.add(trade_reference)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return R.ok(msg="添加数据成功")

    @record_ns.doc("update_record")
    @record_ns.expect(record_models["record_update_model"], validate=False)
    @record_ns.marshal_with(record_models["record_response_model"])
    def put(self):
        """
        更新交易记录

        1. 接口说明
        - 更新已存在的交易记录信息。
        - 支持全量更新关联列表（tradeReferences）。

        2. 请求参数说明
        - id (int, required): 记录ID
        - 其他可选更新字段: transactionsPrice, transactionsShare, transactionsFee, etc.
        - tradeReferences (list, optional): 关联列表，用于全量替换。
          - 列表项格式: {"groupType": int, "groupId": int}

        3. 关键逻辑
        - 如果提供了 tradeReferences，会删除该记录下的所有旧关联，并插入新关联。
        - 会对新关联中的业务对象ID（如网格类型ID）进行存在性校验。

        4. 请求示例
        {
            "id": 1,
            "transactionsPrice": 11000,
            "tradeReferences": [
                {"groupType": 1, "groupId": 10},
                {"groupType": 1, "groupId": 11}
            ]
        }

        5. 返回示例
        {
            "code": 20000,
            "message": "更新数据成功",
            "success": true
        }
        """
        data = RecordUpdateSchema().load(record_ns.payload)
        logger.info(f"更新交易记录, 参数: {data}")
        record_id = data.get("id")
        trade_references = data.get("trade_references")

        # 校验记录是否存在
        record = db.session.get(Record, record_id)
        if not record:
            return R.fail(msg="交易记录不存在")

        try:
            # Update logic
            # Use dictionary directly
            update_data = {
                k: v for k, v in data.items() if k != "id" and k != "trade_references"
            }

            if update_data:
                Record.query.filter(Record.id == record_id).update(update_data)

            # Update Trade References if provided
            if trade_references is not None:
                # 3.1 校验所有新的关联对象是否存在（针对GridType）
                new_refs = []
                seen = set()

                for item in trade_references:
                    group_type = item.get("group_type", 0)
                    group_id = item.get("group_id")

                    # 校验重复
                    key = (group_type, group_id)
                    if key in seen:
                        continue  # 忽略重复项
                    seen.add(key)

                    # 校验GridType
                    if group_type == TradeReferenceGroupTypeEnum.GRID.value:
                        grid_type = db.session.get(GridType, group_id)
                        if not grid_type:
                            raise WebBaseException(msg=f"网格类型ID {group_id} 不存在")

                    new_refs.append(
                        {
                            "record_id": record_id,
                            "group_type": group_type,
                            "group_id": group_id,
                        }
                    )

                # 3.2 删除该记录下的所有旧关联
                TradeReference.query.filter_by(record_id=record_id).delete()

                # 3.3 批量插入新关联
                if new_refs:
                    db.session.bulk_insert_mappings(TradeReference, new_refs)

            db.session.commit()
            return R.ok(msg="更新数据成功")

        except Exception as e:
            db.session.rollback()
            # 如果是 WebBaseException，直接抛出，由全局异常处理
            if isinstance(e, WebBaseException):
                raise e
            return R.fail(msg=f"更新失败: {str(e)}")


@record_ns.route("/<int:record_id>")
class RecordItemRouters(Resource):
    @record_ns.doc("get_record", params={"record_id": "交易记录的唯一标识ID"})
    @record_ns.marshal_with(record_models["record_detail_response_model"])
    def get(self, record_id):
        """
        获取交易记录详情

        1. 接口说明
        - 根据 ID 获取单条交易记录详情。
        - 结果包含基础信息、资产名称、关联的分组类型摘要（groupTypes）和完整的关联详情列表（tradeReferences）。

        2. 路径参数
        - record_id (int, required): 交易记录的唯一标识ID

        3. 返回数据格式
        - success (bool): 是否成功
        - data (object):
            - recordId (int): 记录ID
            - ... (基础字段)
            - groupTypes (list[int]): 关联分组类型列表
            - tradeReferences (list[object]): 关联详情列表
                - id (int): 关联ID
                - groupType (int): 分组类型
                - groupId (int): 业务对象ID
        """
        debug("获取交易记录, /record ,参数：%d" % record_id)
        logger.info(f"获取交易记录详情, ID: {record_id}")

        # 1. 查询基础记录信息
        record_query = (
            db.session.query(
                Record.id.label("record_id"),
                Record.transactions_fee,
                Record.transactions_share,
                Record.transactions_date,
                Record.transactions_price,
                Record.transactions_direction,
                Record.transactions_amount,
                Record.asset_id,
                Asset.asset_name,
            )
            .join(Asset, Record.asset_id == Asset.id)
            .filter(Record.id == record_id)
            .first()
        )

        if not record_query:
            return R.fail(msg="未找到交易记录")

        # 2. 查询所有关联信息
        trade_refs = TradeReference.query.filter_by(record_id=record_id).all()

        # 3. 提取分组类型列表 (去重)
        group_types = list(set([ref.group_type for ref in trade_refs]))

        # 4. 组装 Trade Reference 详情列表
        trade_references_data = []
        for ref in trade_refs:
            trade_references_data.append(
                {
                    "id": ref.id,
                    "recordId": ref.record_id,
                    "groupType": ref.group_type,
                    "groupId": ref.group_id,
                }
            )

        # 5. 组装最终结果
        result = {
            "recordId": record_query.record_id,
            "transactionsFee": str(record_query.transactions_fee),
            "transactionsShare": str(record_query.transactions_share),
            "transactionsDate": record_query.transactions_date.strftime(
                webcons.DataFormatStr.Y_m_d_H_M_S
            ),
            "assetId": record_query.asset_id,
            "transactionsPrice": str(record_query.transactions_price),
            "transactionsDirection": record_query.transactions_direction,
            "transactionsAmount": str(record_query.transactions_amount),
            "assetName": record_query.asset_name,
            "groupTypes": group_types,
            "tradeReferences": trade_references_data,
        }

        return R.ok(data=result)

    @record_ns.doc("delete_record")
    @record_ns.marshal_with(record_models["record_response_model"])
    def delete(self, record_id):
        """
        删除交易记录

        1. 接口说明
        - 根据 ID 删除交易记录，并级联删除关联的 TradeReference。

        2. 返回数据格式
        - 成功响应格式：{"code": 20000, "data": null, "message": "删除数据成功", "success": true}

        3. 路径参数
        - record_id (int, required): 交易记录的唯一标识ID

        4. 请求示例
        - DELETE /api/record/1

        5. 返回示例
        {
            "code": 20000,
            "data": null,
            "message": "删除数据成功",
            "success": true
        }
        """
        logger.info(f"删除交易记录, ID: {record_id}")
        Record.query.filter(Record.id == record_id).delete()
        # 删除关联记录数据
        TradeReference.query.filter(TradeReference.record_id == record_id).delete()
        db.session.commit()
        return R.ok(msg="删除数据成功")


# Keep RecordListRouter and RecordFileRouter on Flask-Restful for now (unless refactoring them too)
# But need to make sure imports match.
# I renamed Resource to RestfulResource for them.


class RecordFileRouter(RestfulResource):
    def post(self):
        """
        @@@
        ### doc
        ```
        Record文件上传接口，上传格式为xlsx，需要包含“交易时间，交易价格，交易份额，交易费用”中文列，可以将'网格名称_网格类型名称'作为工作簿名字，
        也可以不填写工作簿名字，如果不填写工作簿名字，则需要从上传表单中指定名称
        列名说明：
        ...
        ```
        """
        parse = reqparse.RequestParser()
        parse.add_argument("file", required=True, type=FileStorage, location="files")
        parse.add_argument(
            "gridTypeId", required=True, dest="grid_type_id", type=int, location="form"
        )
        parse.add_argument(
            "sheetName", dest="sheet_name", required=False, type=str, location="form"
        )
        args = parse.parse_args()
        grid_type_id = args.get("grid_type_id")
        sheet_name = args.get("sheetName", None)
        # 查询网格信息是否存在
        grid_info = (
            db.session.query(
                Grid.grid_name,
                Grid.id.label("grid_id"),
                GridType.id.label("grid_type_id"),
                GridType.type_name,
                Grid.asset_id,
            )
            .join(GridType, GridType.grid_id == Grid.id, isouter=True)
            .filter(GridType.id == grid_type_id)
            .first()
        )
        if grid_info is None:
            raise WebBaseException(msg="数据错误，网格数据不存在")
        # 如果没有指定工作表名称，则使用网格名称+网格类型名称作为工作表名称
        if sheet_name is None or len(sheet_name) == 0:
            sheet_name = grid_info.grid_name + "_" + grid_info.type_name
        # 读取文件
        df: pd.Datetime = pd.read_excel(args.get("file"), sheet_name=sheet_name)
        convert_record_sync_file_to_list(df, grid_info)
        # records = df.to_json(orient='records')
        records = df.to_dict("records")
        # 清空旧数据
        Record.query.filter(
            and_(
                Record.strategy_type == StrategyEnum.GRID.value,
                Record.strategy_key == grid_type_id,
            )
        ).delete()
        # 清除GridTypeRecord
        GridTypeRecord.query.filter(
            GridTypeRecord.grid_type_id == grid_type_id
        ).delete()
        # 保存数据
        try:
            record_objs = RecordSchema().load(records, many=True)
            db.session.add_all(record_objs)
            db.session.flush()
            # 保存网格类型和交易记录的关联关系
            grid_type_records = [
                GridTypeRecord(grid_type_id=grid_type_id, record_id=record.id)
                for record in record_objs
            ]
            db.session.add_all(grid_type_records)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return R.ok(msg="保存成功， 新增 %d 条交易记录数据" % len(record_objs))


def convert_record_sync_file_to_list(grid_record_df: DataFrame, grid_info) -> list:
    column_set = {"交易时间", "交易价格", "交易份额", "交易费用"}
    if not column_set.issubset(set(grid_record_df.columns)):
        return R.fail(msg="文件格式不正确，缺少必要的列")
    grid_record_df["asset_id"] = grid_info.asset_id
    # 处理时间
    grid_record_df["交易时间"] = pd.to_datetime(
        grid_record_df["交易时间"], infer_datetime_format=True
    ).apply(lambda x: x.strftime(webcons.DataFormatStr.Y_m_d_H_M_S))
    # 计算交易方向
    grid_record_df["交易方向"] = (
        grid_record_df["交易份额"] / abs(grid_record_df["交易份额"])
    ).astype("Int64")
    grid_record_df.loc[grid_record_df["交易方向"] < 0, "交易方向"] = (
        web.common.enum.webEnum.RecordDirectionEnum.SELL.value
    )
    # 处理交易份额的负数
    grid_record_df["交易份额"] = abs(grid_record_df["交易份额"])
    # 处理交易价格、交易费用
    grid_record_df[["交易价格", "交易费用"]] *= 1000
    grid_record_df[["交易价格", "交易费用"]] = (
        grid_record_df[["交易价格", "交易费用"]].round().astype("Int64")
    )
    # 计算交易金额
    grid_record_df["交易金额"] = grid_record_df["交易价格"] * grid_record_df["交易份额"]
    grid_record_df.rename(
        columns={
            "交易时间": "transactions_date",
            "资产ID": "asset_id",
            "交易价格": "transactions_price",
            "交易份额": "transactions_share",
            "交易费用": "transactions_fee",
            "交易方向": "transactions_direction",
            "交易金额": "transactions_amount",
        },
        inplace=True,
    )
    # records = df.to_json(orient='records')
    records: list = grid_record_df.to_dict("records")
    return records


# Removed RecordRouter registration to record_api
# record_api.add_resource(RecordRouter, "", "/<int:record_id>")

record_file_api.add_resource(RecordFileRouter, "")
