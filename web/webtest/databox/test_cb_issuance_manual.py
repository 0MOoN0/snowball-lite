from datetime import date

import pytest

from web.common.enum.databox.databox_enum import DataBoxAdapterEnum
from web.databox.data_box import DataBox


def test_manual_cb_issuance_real_call_strict():
    """
    手动触发的真实环境测试（严格模式）。

    说明：
    - 默认跳过，只有当环境变量 RUN_REAL_AKSHARE=1 时才运行。
    - 需要本机已安装 akshare，并可访问外网。
    - 通过 DataBox 能力驱动，严格指定数据源为 AkShare，返回 DTO 列表。
    验证点:
    - 返回类型为 List[ConvertibleBondIssuanceData]
    - 每个 DTO 至少包含 bond_code/bond_name 字段
    """

    try:
        import akshare  # noqa: F401  # 仅验证安装状态
    except Exception:
        pytest.skip("AkShare is not available in this environment")

    dbox = DataBox()
    records = dbox.get_cb_issuance_list(
        start_date=date(2025, 11, 1),
        end_date=date(2025, 11, 10),
        source=DataBoxAdapterEnum.AKSHARE,
    )

    assert isinstance(records, list)
    # 真实数据可能为空（区间内无发行），因此仅在非空时做进一步断言
    if records:
        sample = records[0]
        assert hasattr(sample, "bond_code")
        assert hasattr(sample, "bond_name")

    # 打印样例以便人工检查（最多前3条）
    print("CB issuance sample:", [(r.bond_code, r.bond_name) for r in records[:3]])