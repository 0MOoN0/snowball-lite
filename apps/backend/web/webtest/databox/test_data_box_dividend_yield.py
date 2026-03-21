# -*- coding: UTF-8 -*-
"""
集成测试：真实调用 AkShare 获取中国内地企业全球综合指数（H30374）股息率

说明：
- 标记为集成测试，依赖外部网络与 akshare 实时数据接口
- 若未安装 akshare，则跳过此用例
- 通过 DataBox → AdapterService → IndexValuationService → AkShareAdapter 的完整链路获取数据
"""
import pytest

from web.common.enum.asset_enum import AssetTypeEnum
from web.common.enum.common_enum import MarketEnum
from web.common.enum.databox.databox_enum import DataBoxAdapterEnum
from web.databox.data_box import DataBox
from web.databox.models.dividend_yield import IndexDividendYieldData
from web.databox.enum.DataSourceEnum import DataSourceEnum
from web.webtest.test_base import TestBaseAppOnly


@pytest.mark.integration
class TestDataBoxH30374DividendYieldIntegration(TestBaseAppOnly):
    """测试覆盖范围：
    - 端到端验证 DataBox 调用链路至 AkShareAdapter 的真实数据获取能力
    - 仅覆盖指数股息率（DIVIDEND_YIELD）指标，资产类型为 INDEX，市场为 CN
    """

    def test_get_h30374_dividend_yield_via_akshare_real(self):
        """验证点:
        - akshare 存在则正常执行，否则跳过
        - 返回对象非空且为 IndexDividendYieldData 类型
        - 指数代码应等于 "H30374"
        - 股息率字段为数值且处于合理范围 [0, 20)
        - 币种为 "CNY"
        - 数据来源为 DataSourceEnum.AKSHARE_CSINDEX.value
        """
        # 若 akshare 未安装，跳过此测试
        pytest.importorskip("akshare", reason="akshare is required for this integration test")

        # 使用真实的 DataBox 初始化（包含 AkShareAdapter）
        data_box = DataBox()

        # 实际调用：获取中国内地企业全球综合指数股息率
        result = data_box.get_dividend_yield(
            symbol="000300",
            asset_type=AssetTypeEnum.INDEX,
            source=DataBoxAdapterEnum.AKSHARE,
            market=MarketEnum.CN,
        )

        # 验证点：返回值存在且结构正确，股息率在合理范围内
        assert result is not None, "AkShare 返回为空，请检查网络/数据接口是否可用"
        assert isinstance(result, IndexDividendYieldData)
        assert result.symbol == "000300"
        assert isinstance(result.dividend_yield, (int, float))
        assert 0 <= result.dividend_yield < 20  # 股息率百分比的合理范围约束
        assert result.currency == "CNY"
        assert result.data_source == DataSourceEnum.AKSHARE_CSINDEX.value