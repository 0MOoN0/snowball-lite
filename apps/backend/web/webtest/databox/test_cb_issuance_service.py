from datetime import date

import pandas as pd

from web.databox.adapter.data.AkShareAdapter import AkShareAdapter
from web.databox.data_box import DataBox


def test_get_cb_issuance_list_returns_dto(monkeypatch):
    """
    验证点:
    - DataBox.get_cb_issuance_list 返回 DTO 列表而非 DataFrame
    - AkShareAdapter 将 bond_cov_issue_cninfo DataFrame 正确映射为 ConvertibleBondIssuanceData
    - 日期与数值字段被正确解析
    """

    # 构造模拟的 cninfo 返回数据
    df = pd.DataFrame([
        {
            "债券代码": "123456",
            "债券简称": "示例转债",
            "交易市场": "上交所",
            "债券名称": "2024年示例公司可转换公司债券",
            "公告日期": "2024-10-01",
            "发行规模(亿元)": 10.5,
            "发行价格(元)": 100,
        }
    ])

    # Mock AkShare 调用以避免真实网络请求
    monkeypatch.setattr(
        AkShareAdapter,
        "get_cb_issuance_cninfo",
        lambda self, start_date, end_date: df,
    )

    dbox = DataBox()
    records = dbox.get_cb_issuance_list(
        start_date=date(2024, 10, 1), end_date=date(2024, 10, 31)
    )

    assert isinstance(records, list)
    assert len(records) == 1

    dto = records[0]
    assert dto.bond_code == "123456"
    assert dto.bond_name == "示例转债"
    assert dto.full_name == "2024年示例公司可转换公司债券"
    # 市场值为原始映射字符串
    assert dto.issue_date == date(2024, 10, 1)
    assert dto.issue_amount == 10.5
    assert dto.issue_price == 100.0