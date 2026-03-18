from io import BytesIO
import time
from decimal import Decimal
from flask import request, send_file
from flask_restx import Namespace, Resource
from sqlalchemy import and_

import pandas as pd

from web.common.api_factory import get_api
from web.models import db
from web.models.asset.asset import Asset
from web.models.asset.asset_alias import AssetAlias
from web.models.record.record import Record
from web.models.record.trade_reference import TradeReference
from web.routers.record.record_file_schemas import (
    RecordFileRequestSchema,
    RecordImportRequestSchema,
    create_record_file_models,
    create_upload_parser,
)
from web.services.record.record_import_service import RecordImportService
from web.weblogger import logger
from web.common.utils import R

record_file_ns = Namespace("record_file", description="交易记录文件管理")

api = get_api()
if api:
    api.add_namespace(record_file_ns, path="/api/record_file")

record_file_models = create_record_file_models(record_file_ns)


def _build_record_query(args):
    """
    构建交易记录查询对象
    :param args: 筛选参数字典
    :return: SQLAlchemy Query对象
    """
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
    if group_type is not None:
        query = query.join(TradeReference, TradeReference.record_id == Record.id)
        query = query.filter(TradeReference.group_type == group_type)
        if group_id is not None:
            query = query.filter(TradeReference.group_id == group_id)

    # 2. 筛选条件：资产名称
    if asset_name:
        query = query.filter(Asset.asset_name.like(f"%{asset_name}%"))

    # 2.1 筛选条件：资产别名
    if asset_alias:
        alias_exists = (
            db.session.query(AssetAlias)
            .filter(
                AssetAlias.asset_id == Asset.id,
                AssetAlias.provider_symbol.like(f"%{asset_alias}%"),
                AssetAlias.status == 1,
            )
            .exists()
        )
        query = query.filter(alias_exists.correlate(Asset))

    # 3. 筛选条件：时间范围
    if start_date:
        query = query.filter(Record.transactions_date >= start_date)
    if end_date:
        query = query.filter(Record.transactions_date <= end_date)

    # 4. 筛选条件：交易方向
    if transactions_direction is not None:
        query = query.filter(Record.transactions_direction == transactions_direction)

    return query


@record_file_ns.route("/export/check")
class RecordExportCheckRouter(Resource):
    """
    导出前检查
    """

    @record_file_ns.doc(
        "check_export_records",
        params={
            "groupType": "分组类型（如 1-网格），用于筛选特定业务类型的记录",
            "groupId": "业务对象ID，需配合 groupType 使用（筛选特定关联ID）",
            "assetName": "资产名称（模糊查询）",
            "assetAlias": "资产别名（模糊查询）",
            "startDate": "开始时间 (yyyy-MM-dd HH:mm:ss)",
            "endDate": "结束时间 (yyyy-MM-dd HH:mm:ss)",
            "transactionsDirection": "交易方向 (0:卖出, 1:买入)",
        },
    )
    @record_file_ns.marshal_with(record_file_models["export_check_response_model"])
    def get(self):
        """
        查询符合导出条件的记录数量

        1. 接口说明
        - 用于导出前检查，返回符合条件的记录总数。
        - 筛选条件与导出接口完全一致。

        2. 返回数据
        - {"code": 20000, "data": {"count": 100}, "success": true}
        """
        args = RecordFileRequestSchema().load(request.args.to_dict())
        logger.info(f"检查导出记录数量, 参数: {args}")

        query = _build_record_query(args)
        count = query.count()

        return R.ok(data={"count": count})


@record_file_ns.route("/export")
class RecordExportRouter(Resource):
    """
    导出交易记录
    """

    @record_file_ns.doc(
        "export_records",
        params={
            "groupType": "分组类型（如 1-网格），用于筛选特定业务类型的记录",
            "groupId": "业务对象ID，需配合 groupType 使用（筛选特定关联ID）",
            "assetName": "资产名称（模糊查询）",
            "assetAlias": "资产别名（模糊查询）",
            "startDate": "开始时间 (yyyy-MM-dd HH:mm:ss)",
            "endDate": "结束时间 (yyyy-MM-dd HH:mm:ss)",
            "transactionsDirection": "交易方向 (0:卖出, 1:买入)",
        },
    )
    def get(self):
        """
        导出交易记录为Excel

        1. 接口说明
        - 导出交易记录为Excel文件，支持多维度筛选。
        - 筛选条件与交易记录列表接口一致。
        - 默认按交易时间倒序排列。

        2. 请求参数说明
        - groupType (int, optional): 分组类型（如 1-网格），用于筛选特定业务类型的记录
        - groupId (int, optional): 业务对象ID，需配合 groupType 使用（筛选特定关联ID）
        - assetName (str, optional): 资产名称（模糊查询）
        - assetAlias (str, optional): 资产别名（模糊查询）
        - startDate (str, optional): 开始时间 (yyyy-MM-dd HH:mm:ss)
        - endDate (str, optional): 结束时间 (yyyy-MM-dd HH:mm:ss)
        - transactionsDirection (int, optional): 交易方向 (0:卖出, 1:买入)

        3. 返回数据
        - 文件流: .xlsx 格式的Excel文件
        """
        args = RecordFileRequestSchema().load(request.args.to_dict())
        logger.info(f"导出交易记录, 参数: {args}")

        query = _build_record_query(args)

        # 获取所有数据
        records = query.order_by(Record.transactions_date.desc()).all()

        # 转换为DataFrame
        data_list = []
        for r in records:
            direction_str = "买入" if r.transactions_direction == 1 else "卖出"

            # 金额单位处理：厘 -> 元 (使用Decimal处理)
            fee = (
                Decimal(r.transactions_fee) / Decimal(1000)
                if r.transactions_fee is not None
                else Decimal(0)
            )
            price = (
                Decimal(r.transactions_price) / Decimal(1000)
                if r.transactions_price is not None
                else Decimal(0)
            )
            amount = (
                Decimal(r.transactions_amount) / Decimal(1000)
                if r.transactions_amount is not None
                else Decimal(0)
            )

            item = {
                "资产名称": r.asset_name,
                "资产代码": r.primary_alias_code,
                "交易时间": r.transactions_date,
                "交易方向": direction_str,
                "交易价格(元)": price,
                "交易份额": r.transactions_share,
                "交易金额(元)": amount,
                "交易费用(元)": fee,
                "提供商": r.primary_provider_name,
            }
            data_list.append(item)

        df = pd.DataFrame(data_list)

        # 如果没有数据，创建一个空的DataFrame，但带有表头
        if df.empty:
            df = pd.DataFrame(
                columns=[
                    "资产名称",
                    "资产代码",
                    "交易时间",
                    "交易方向",
                    "交易价格(元)",
                    "交易份额",
                    "交易金额(元)",
                    "交易费用(元)",
                    "提供商",
                ]
            )

        # 导出为Excel
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        df.to_excel(writer, sheet_name="交易记录", index=False)
        writer.close()
        output.seek(0)

        filename = f'交易记录_{time.strftime("%Y%m%d%H%M%S")}.xlsx'

        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename,
        )



upload_parser = create_upload_parser(record_file_ns)



@record_file_ns.route("/import/preview")
class RecordImportPreviewRouter(Resource):
    @record_file_ns.doc("import_preview")
    @record_file_ns.expect(upload_parser, validate=False)
    @record_file_ns.marshal_with(record_file_models["import_preview_response_model"])
    def post(self):
        """
        导入预览

        1. 接口说明
        - 上传Excel文件，解析并预览数据。
        - 自动匹配资产，返回匹配结果及状态。
        - 支持的列名：成交日期, 成交时间, 证券代码, 证券名称, 委托类别, 成交价格, 成交数量, 发生金额, 佣金
        - 支持传入 provider_code (如 'THS', 'SNOWBALL'等) 来辅助匹配

        2. 请求参数
        - file: Excel文件
        - providerCode: 数据提供商代码 (可选)

        3. 返回数据
        - row_index: 行号
        - status: valid(正常)/error(错误)/warning(警告)
        - message: 提示信息
        - parsed_data: 解析后的数据（用于确认导入）
        """
        if "file" not in request.files:
            return R.fail("未上传文件")

        file = request.files["file"]
        if file.filename == "":
            return R.fail("未选择文件")

        # Do not use parser.parse_args() as per project rules (NO reqparse)
        provider_code = request.form.get("providerCode")

        try:
            result = RecordImportService.parse_and_preview(file, provider_code)
            return R.ok(data=result)
        except Exception as e:
            logger.error(f"预览失败: {e}", exc_info=True)
            return R.fail(f"预览失败: {str(e)}")


@record_file_ns.route("/import/confirm")
class RecordImportConfirmRouter(Resource):
    @record_file_ns.doc("import_confirm")
    @record_file_ns.expect(record_file_models["import_confirm_request_model"], validate=False)
    @record_file_ns.marshal_with(record_file_models["import_confirm_response_model"])
    def post(self):
        """
        导入确认

        1. Params:
        - importMode (int, optional): 导入模式. 0=增量(默认), 1=全量覆盖(按资产), 2=部分替换(按资产+时间范围), 3=范围替换(按指定时间范围).
        - rangeStart (str, optional): 替换范围开始时间 (yyyy-MM-dd HH:mm:ss), 当 importMode=3 时必填.
        - rangeEnd (str, optional): 替换范围结束时间 (yyyy-MM-dd HH:mm:ss), 当 importMode=3 时必填.
        - items (list, required): 记录列表. 每一项需包含解析后的关键字段.
            - assetId (int, required): 资产ID
            - transactionsDate (str, required): 交易时间
            - transactionsPrice (int, required): 交易价格(厘)
            - transactionsShare (int, required): 交易份额
            - transactionsDirection (int, required): 交易方向
            - transactionsAmount (int, required): 交易金额(厘)
            - groups (list, optional): 关联分组列表 `[{groupType, groupId}]`.

        2. Response:
        - Success: {"code": 20000, "success": true, "message": "操作成功", "data": 10}  # 成功导入条数
        - Fail: {"code": 50000, "success": false, "message": "导入失败: ...", "data": null}

        3. Notes:
        - importMode=1 (OVERWRITE): 删除导入数据中涉及资产的所有旧记录，然后插入新记录。
        - importMode=2 (REPLACE): 删除导入数据中涉及资产在导入数据时间范围内的旧记录，然后插入新记录。
        - importMode=3 (REPLACE_RANGE): 删除导入数据中涉及资产在 `[rangeStart, rangeEnd]` 时间范围内的旧记录，然后插入新记录。
        - importMode=0 (APPEND): 直接追加新记录，不去重。
        """
        # Validate using Marshmallow
        try:
            req_data = RecordImportRequestSchema().load(record_file_ns.payload)
            data = req_data["items"]
            import_mode = req_data.get("import_mode", 0)
            range_start = req_data.get("range_start")
            range_end = req_data.get("range_end")
        except Exception as e:
            return R.fail(f"数据验证失败: {str(e)}")

        try:
            count = RecordImportService.import_records(
                data,
                import_mode=import_mode,
                range_start=range_start,
                range_end=range_end
            )
            return R.ok(data=count)
        except Exception as e:
            logger.error(f"导入失败: {e}", exc_info=True)
            return R.fail(f"导入失败: {str(e)}")
