from marshmallow import Schema, fields, pre_load, post_load
from datetime import datetime, date
from web.databox.models.dto.convertible_bond_issuance import ConvertibleBondIssuanceData


class ConvertibleBondIssuanceSchema(Schema):
    # 基本信息
    bond_code = fields.String(required=True, data_key="债券代码")
    bond_name = fields.String(required=True, data_key="债券简称")
    market = fields.String(allow_none=True, data_key="交易市场")
    full_name = fields.String(allow_none=True, data_key="债券名称")

    # 日期（以字符串接收，适配不同格式；在适配器中统一解析为 date）
    # 使用 Raw 接受任意类型（datetime.date/str/Timestamp），在适配器中统一解析为 date
    # 使用 Raw 接受 datetime.date/str/Timestamp；尽量不做转换，保持简单
    issue_date = fields.Raw(allow_none=True, data_key="公告日期")
    issue_start_date = fields.Raw(allow_none=True, data_key="发行起始日")
    issue_end_date = fields.Raw(allow_none=True, data_key="发行终止日")
    convert_start_date = fields.Raw(allow_none=True, data_key="转股开始日期")
    convert_end_date = fields.Raw(allow_none=True, data_key="转股终止日期")
    convert_happen_date = fields.Raw(allow_none=True, data_key="转股发生日")
    online_subscribe_date = fields.Raw(allow_none=True, data_key="网上申购日期")
    online_result_announce_and_refund_date = fields.Raw(allow_none=True, data_key="网上申购中签结果公告日及退款日")
    priority_subscribe_date = fields.Raw(allow_none=True, data_key="优先申购日")
    bond_register_date = fields.Raw(allow_none=True, data_key="债权登记日")
    priority_subscribe_payment_date = fields.Raw(allow_none=True, data_key="优先申购缴款日")

    # 数值与文本（保持原始单位）
    planned_total_amount = fields.Float(allow_none=True, data_key="计划发行总量")
    actual_total_amount = fields.Float(allow_none=True, data_key="实际发行总量")
    par_value = fields.Integer(allow_none=True, data_key="发行面值")
    issue_price = fields.Float(allow_none=True, data_key="发行价格")
    issue_method = fields.String(allow_none=True, data_key="发行方式")
    issue_target = fields.String(allow_none=True, data_key="发行对象")
    issue_scope = fields.String(allow_none=True, data_key="发行范围")
    underwriting_method = fields.String(allow_none=True, data_key="承销方式")
    use_of_proceeds = fields.String(allow_none=True, data_key="募资用途说明")
    initial_conversion_price = fields.Float(allow_none=True, data_key="初始转股价格")
    online_subscribe_code = fields.String(allow_none=True, data_key="网上申购代码")
    online_subscribe_name = fields.String(allow_none=True, data_key="网上申购简称")
    online_subscribe_upper_limit = fields.Float(allow_none=True, data_key="网上申购数量上限")
    online_subscribe_lower_limit = fields.Float(allow_none=True, data_key="网上申购数量下限")
    online_subscribe_unit = fields.Float(allow_none=True, data_key="网上申购单位")
    placement_price = fields.Float(allow_none=True, data_key="配售价格")
    convert_code = fields.String(allow_none=True, data_key="转股代码")

    # 兼容旧版本字段
    issue_amount = fields.Float(allow_none=True, data_key="发行规模(亿元)")

    @pre_load
    def compat_issue_date(self, data, **kwargs):
        # 若不存在“公告日期”但存在“发行日期”，则复用为 issue_date
        if "公告日期" not in data and "发行日期" in data:
            data["公告日期"] = data.get("发行日期")
        # 仅处理空值别名，不做强制解析，保持简单
        for k in [
            "公告日期", "发行起始日", "发行终止日", "转股开始日期", "转股终止日期", "转股发生日",
            "网上申购日期", "网上申购中签结果公告日及退款日", "优先申购日", "债权登记日", "优先申购缴款日",
        ]:
            v = data.get(k)
            if isinstance(v, str) and v.strip() in {"", "-", "—", "NaT", "None", "null"}:
                data[k] = None
        return data

    class Meta:
        # 忽略未知字段，避免抛错导致整体回退为最小字典
        unknown = "EXCLUDE"

    @post_load
    def make_dto(self, data, **kwargs) -> ConvertibleBondIssuanceData:
        # 由 Schema 直接构造 DTO，并补充数据来源与更新时间
        dto = ConvertibleBondIssuanceData(**data)
        ds = getattr(self, "context", {}).get("data_source")
        if ds:
            dto.data_source = ds
        dto.update_time = datetime.now()
        return dto