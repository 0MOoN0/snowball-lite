from datetime import datetime
from marshmallow import Schema, fields, post_load, ValidationError
from flask_restx import fields as restx_fields
from web.routers.common.response_schemas import create_typed_response_model
from web.common.cons import webcons
from web.services.record.record_dtos import RecordImportDTO, RecordGroupDTO


class RecordFileRequestSchema(Schema):
    group_type = fields.Integer(
        data_key="groupType", load_default=None, description="分组类型: 0-其他, 1-网格"
    )
    group_id = fields.Integer(
        data_key="groupId", load_default=None, description="业务对象ID"
    )
    asset_name = fields.String(
        data_key="assetName", load_default=None, description="资产名称（模糊查询）"
    )
    asset_alias = fields.String(
        data_key="assetAlias", load_default=None, description="资产别名（模糊查询）"
    )
    start_date = fields.String(
        data_key="startDate", load_default=None, description="交易开始时间"
    )
    end_date = fields.String(
        data_key="endDate", load_default=None, description="交易结束时间"
    )
    transactions_direction = fields.Integer(
        data_key="transactionsDirection", load_default=None, description="交易方向"
    )

    class Meta:
        unknown = "EXCLUDE"


class RecordGroupSchema(Schema):
    group_type = fields.Integer(required=True, description="关联分组类型", data_key="groupType")
    group_id = fields.Integer(required=True, description="关联分组ID", data_key="groupId")

    @post_load
    def make_dto(self, data, **kwargs):
        return RecordGroupDTO(**data)


class RecordImportItemSchema(Schema):
    asset_id = fields.Integer(required=True, description="资产ID", data_key="assetId")
    transactions_date = fields.String(
        required=True, description="交易时间", data_key="transactionsDate"
    )
    transactions_price = fields.Integer(
        required=True, description="交易价格(厘)", data_key="transactionsPrice"
    )
    transactions_share = fields.Integer(
        required=True, description="交易份额", data_key="transactionsShare"
    )
    transactions_fee = fields.Integer(
        load_default=0, description="交易费用(厘)", data_key="transactionsFee"
    )
    transactions_direction = fields.Integer(
        required=True, description="交易方向", data_key="transactionsDirection"
    )
    transactions_amount = fields.Integer(
        required=True, description="交易金额(厘)", data_key="transactionsAmount"
    )
    groups = fields.List(
        fields.Nested(RecordGroupSchema),
        load_default=list,
        description="关联分组列表",
        data_key="groups"
    )

    @post_load
    def make_dto(self, data, **kwargs):
        trans_date_str = data.get("transactions_date")
        if isinstance(trans_date_str, str):
            try:
                data["transactions_date"] = datetime.strptime(
                    trans_date_str, webcons.DataFormatStr.Y_m_d_H_M_S
                )
            except ValueError:
                try:
                    data["transactions_date"] = datetime.strptime(
                        trans_date_str, webcons.DataFormatStr.Y_m_d
                    )
                except ValueError:
                    raise ValidationError(f"日期格式错误: {trans_date_str}")
        
        return RecordImportDTO(**data)

    class Meta:
        unknown = "EXCLUDE"


class RecordImportRequestSchema(Schema):
    import_mode = fields.Integer(
        load_default=0,
        description="导入模式: 0-增量, 1-全量覆盖, 2-部分替换, 3-范围替换",
        data_key="importMode"
    )
    range_start = fields.String(
        load_default=None,
        description="替换范围开始时间 (yyyy-MM-dd HH:mm:ss)",
        data_key="rangeStart"
    )
    range_end = fields.String(
        load_default=None,
        description="替换范围结束时间 (yyyy-MM-dd HH:mm:ss)",
        data_key="rangeEnd"
    )
    items = fields.List(
        fields.Nested(RecordImportItemSchema),
        required=True,
        description="记录列表",
        data_key="items"
    )

    class Meta:
        unknown = "EXCLUDE"


def create_record_file_models(api):
    export_check_data_model = api.model(
        "ExportCheckData",
        {
            "count": restx_fields.Integer(
                description="符合条件的记录总数", example=100
            ),
        },
    )

    export_check_response_model = create_typed_response_model(
        export_check_data_model, "_ExportCheck"
    )

    # Preview Models
    import_preview_raw_data_model = api.model(
        "ImportPreviewRawData",
        {
            "成交日期": restx_fields.String(description="成交日期"),
            "成交时间": restx_fields.String(description="成交时间"),
            "证券代码": restx_fields.String(description="证券代码"),
            "证券名称": restx_fields.String(description="证券名称"),
            "委托类别": restx_fields.String(description="委托类别"),
            "成交价格": restx_fields.String(description="成交价格"),
            "成交数量": restx_fields.String(description="成交数量"),
            "发生金额": restx_fields.String(description="发生金额"),
            "佣金": restx_fields.String(description="佣金"),
            "成交编号": restx_fields.String(description="成交编号"),
        },
    )

    import_preview_parsed_data_model = api.model(
        "ImportPreviewParsedData",
        {
            "assetId": restx_fields.Integer(description="资产ID", attribute="asset_id"),
            "assetName": restx_fields.String(description="资产名称", attribute="asset_name"),
            "transactionsDate": restx_fields.String(
                description="交易时间", attribute="transactions_date"
            ),
            "transactionsPrice": restx_fields.Integer(
                description="交易价格(厘)", attribute="transactions_price"
            ),
            "transactionsShare": restx_fields.Integer(
                description="交易份额", attribute="transactions_share"
            ),
            "transactionsAmount": restx_fields.Integer(
                description="交易金额(厘)", attribute="transactions_amount"
            ),
            "transactionsFee": restx_fields.Integer(
                description="交易费用(厘)", attribute="transactions_fee"
            ),
            "transactionsDirection": restx_fields.Integer(
                description="交易方向", attribute="transactions_direction"
            ),
            "matchSource": restx_fields.String(
                description="匹配来源: provider_symbol/global_symbol/asset_name",
                attribute="match_source",
            ),
        },
    )

    import_preview_item_model = api.model(
        "ImportPreviewItem",
        {
            "rowIndex": restx_fields.Integer(description="行号", attribute="row_index"),
            "status": restx_fields.String(description="状态: valid/error/warning"),
            "message": restx_fields.String(description="提示信息"),
            "rawData": restx_fields.Nested(
                import_preview_raw_data_model, description="原始数据", attribute="raw_data"
            ),
            "parsedData": restx_fields.Nested(
                import_preview_parsed_data_model,
                description="解析后的数据",
                attribute="parsed_data",
            ),
        },
    )

    import_preview_response_model = create_typed_response_model(
        restx_fields.List(restx_fields.Nested(import_preview_item_model)),
        "_ImportPreview",
    )

    # Import Confirm Models
    import_group_item_model = api.model(
        "ImportGroupItem",
        {
            "groupType": restx_fields.Integer(description="关联分组类型"),
            "groupId": restx_fields.Integer(description="关联分组ID"),
        }
    )

    import_confirm_item_model = api.model(
        "ImportConfirmItem",
        {
            "assetId": restx_fields.Integer(required=True, description="资产ID"),
            "transactionsDate": restx_fields.String(
                required=True, description="交易时间"
            ),
            "transactionsPrice": restx_fields.Integer(
                required=True, description="交易价格(厘)"
            ),
            "transactionsShare": restx_fields.Integer(
                required=True, description="交易份额"
            ),
            "transactionsFee": restx_fields.Integer(description="交易费用(厘)"),
            "transactionsDirection": restx_fields.Integer(
                required=True, description="交易方向"
            ),
            "transactionsAmount": restx_fields.Integer(
                required=True, description="交易金额(厘)"
            ),
            "groups": restx_fields.List(
                restx_fields.Nested(import_group_item_model),
                description="关联分组列表"
            ),
        },
    )

    import_confirm_request_model = api.model(
        "ImportConfirmRequest",
        {
            "importMode": restx_fields.Integer(
                description="导入模式: 0-增量, 1-全量覆盖, 2-部分替换, 3-范围替换", default=0
            ),
            "rangeStart": restx_fields.String(description="替换范围开始时间 (yyyy-MM-dd HH:mm:ss)"),
            "rangeEnd": restx_fields.String(description="替换范围结束时间 (yyyy-MM-dd HH:mm:ss)"),
            "items": restx_fields.List(
                restx_fields.Nested(import_confirm_item_model),
                required=True,
                description="记录列表"
            ),
        }
    )

    import_confirm_response_model = create_typed_response_model(
        restx_fields.Integer(description="成功导入条数"), "_ImportConfirm"
    )

    return {
        "export_check_response_model": export_check_response_model,
        "import_preview_response_model": import_preview_response_model,
        "import_confirm_item_model": import_confirm_item_model,
        "import_confirm_request_model": import_confirm_request_model,
        "import_confirm_response_model": import_confirm_response_model,
    }


def create_upload_parser(api):
    from werkzeug.datastructures import FileStorage

    upload_parser = api.parser()
    upload_parser.add_argument(
        "file", location="files", type=FileStorage, required=True, help="Excel file"
    )
    upload_parser.add_argument(
        "providerCode",
        location="form",
        type=str,
        required=False,
        help="数据提供商代码 (可选)",
    )
    return upload_parser
