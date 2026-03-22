from __future__ import annotations

from datetime import date, datetime
from unittest.mock import patch

import pandas as pd
import pytest

from web.common.enum.asset_enum import AssetTypeEnum
from web.common.enum.business.record.trade_reference_enum import (
    TradeReferenceGroupTypeEnum,
)
from web.models import db
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.asset.asset import Asset
from web.models.asset.asset_alias import AssetAlias
from web.models.asset.asset_code import AssetCode
from web.models.asset.asset_fund import AssetFund
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.record.record import Record
from web.models.record.trade_reference import TradeReference
from web.services.analysis.transaction_analysis_service import (
    GridTransactionAnalysisService,
    GridTypeTransactionAnalysisService,
)


pytestmark = [pytest.mark.local, pytest.mark.integration]


FIXED_REGRESSION_COMMAND = (
    "pytest web/webtest/stage4/test_task01_asset_management_sqlite.py "
    "web/webtest/stage4/test_task02_record_management_sqlite.py "
    "web/webtest/stage4/test_task03_analysis_capability_sqlite.py -q && "
    "pytest web/webtest/lite/test_lite_stage4_query_api_matrix.py "
    "tests/test_lite_databox_stage4_coverage.py "
    "web/webtest/lite/test_lite_smoke_validation_and_decision.py "
    "tests/test_xalpha_databox_compat.py -q"
)


QUERY_API_COVERAGE_MATRIX = [
    {
        "capability": "资产查询",
        "entry": "GET /api/asset/list/，GET /api/asset/<asset_id>",
        "automation": "web/webtest/stage4/test_task01_asset_management_sqlite.py",
        "manual": "否",
        "status": "已覆盖（列表/详情自动化；未覆盖 select、alias 列表等扩展查询）",
    },
    {
        "capability": "交易记录查询",
        "entry": "GET /api/record/<record_id>，GET /api/record_list",
        "automation": "web/webtest/stage4/test_task02_record_management_sqlite.py",
        "manual": "否",
        "status": "已覆盖（代表性筛选自动化；未覆盖全部筛选组合）",
    },
    {
        "capability": "分析结果查询",
        "entry": "GET /api/analysis/grid-result/<grid_id>，GET /api/analysis/grid-type-result/<grid_type_id>",
        "automation": "web/webtest/stage4/test_task03_analysis_capability_sqlite.py",
        "manual": "否",
        "status": "已覆盖",
    },
    {
        "capability": "系统查询入口 smoke",
        "entry": "GET /token_test/result",
        "automation": "web/webtest/lite/test_lite_smoke_validation_and_decision.py，web/webtest/lite/test_lite_stage4_query_api_matrix.py",
        "manual": "否",
        "status": "已覆盖（smoke；不是业务查询主面）",
    },
    {
        "capability": "查询读路径辅助链路",
        "entry": "DataBox.fund_info，XaDataAdapter.get_daily，XaServiceAdapter.get_daily，跨 app cache 读取路径",
        "automation": "tests/test_lite_databox_stage4_coverage.py，tests/test_xalpha_databox_compat.py",
        "manual": "是（仅作缓存/运行时抽查，不放进 HTTP 查询面主表）",
        "status": "已覆盖（辅助链路，含 xalpha compat 读取路径）",
    },
]


def _seed_asset_query_data() -> int:
    asset = AssetFund(
        asset_name="阶段4查询矩阵基金",
        asset_code="000001",
        asset_short_code="QRY4",
        asset_type=AssetTypeEnum.FUND.value,
        asset_status=0,
        currency=0,
        market=0,
        fund_type="STOCK_FUND",
        trading_mode="OPEN_END",
        fund_status=0,
        fund_company="阶段4查询矩阵基金公司",
        fund_manager="阶段4查询矩阵基金经理",
    )
    db.session.add(asset)
    db.session.flush()

    db.session.add(
        AssetAlias(
            asset_id=asset.id,
            provider_code="manual",
            provider_symbol="000001",
            provider_name="manual",
            is_primary=True,
            status=1,
        )
    )
    db.session.add(
        AssetCode(
            asset_id=asset.id,
            code_ttjj="F000001",
            code_xq="000001",
        )
    )
    db.session.commit()
    return asset.id


def _seed_record_query_data():
    asset = Asset(
        asset_name="阶段4查询矩阵记录资产",
        asset_type=2,
        asset_status=0,
        currency=0,
        market=0,
    )
    db.session.add(asset)
    db.session.flush()

    db.session.add(
        AssetAlias(
            asset_id=asset.id,
            provider_code="manual",
            provider_symbol="REC-001",
            provider_name="manual",
            is_primary=True,
            status=1,
        )
    )
    db.session.flush()

    grid = Grid(grid_name="阶段4查询矩阵网格", asset_id=asset.id)
    db.session.add(grid)
    db.session.flush()

    grid_type_one = GridType(
        grid_id=grid.id,
        asset_id=asset.id,
        type_name="阶段4查询矩阵网格类型一",
        grid_type_status=0,
    )
    grid_type_two = GridType(
        grid_id=grid.id,
        asset_id=asset.id,
        type_name="阶段4查询矩阵网格类型二",
        grid_type_status=0,
    )
    db.session.add_all([grid_type_one, grid_type_two])
    db.session.flush()

    record_one = Record(
        asset_id=asset.id,
        transactions_date=datetime(2024, 1, 1, 10, 0, 0),
        transactions_fee=10,
        transactions_share=100,
        transactions_price=10000,
        transactions_direction=1,
        transactions_amount=1000000,
    )
    record_two = Record(
        asset_id=asset.id,
        transactions_date=datetime(2024, 1, 2, 10, 0, 0),
        transactions_fee=20,
        transactions_share=200,
        transactions_price=12000,
        transactions_direction=0,
        transactions_amount=2400000,
    )
    db.session.add_all([record_one, record_two])
    db.session.flush()

    db.session.add_all(
        [
            TradeReference(
                record_id=record_one.id,
                group_type=TradeReferenceGroupTypeEnum.GRID.value,
                group_id=grid_type_one.id,
            ),
            TradeReference(
                record_id=record_two.id,
                group_type=TradeReferenceGroupTypeEnum.GRID.value,
                group_id=grid_type_two.id,
            ),
        ]
    )
    db.session.commit()

    return {
        "asset_id": asset.id,
        "asset_name": asset.asset_name,
        "asset_alias": "REC-001",
        "grid_type_one_id": grid_type_one.id,
        "grid_type_two_id": grid_type_two.id,
        "record_two_id": record_two.id,
    }


def _seed_analysis_query_data():
    analysis_date = date(2024, 1, 15)
    asset = Asset(
        asset_code="000001",
        asset_name="阶段4查询矩阵分析资产",
        asset_type=1,
        currency=1,
        market=1,
        asset_status=0,
    )
    db.session.add(asset)
    db.session.flush()

    db.session.add(AssetCode(code_xq="000001", asset_id=asset.id))
    db.session.flush()

    grid = Grid(
        grid_name="阶段4查询矩阵分析网格",
        asset_id=asset.id,
        grid_status=Grid.get_status_enum().ENABLE.value,
    )
    db.session.add(grid)
    db.session.flush()

    grid_type = GridType(
        grid_id=grid.id,
        grid_type_status=0,
        type_name="阶段4查询矩阵分析网格类型",
        asset_id=asset.id,
    )
    db.session.add(grid_type)
    db.session.flush()

    db.session.add(
        GridTypeDetail(
            grid_type_id=grid_type.id,
            grid_id=grid.id,
            gear="1",
            monitor_type=GridTypeDetail.get_monitor_type_enum().SELL.value,
            trigger_sell_price=11000,
            sell_price=11000,
            sell_shares=1000,
            actual_sell_shares=1000,
            sell_amount=11000000,
            trigger_purchase_price=9000,
            purchase_price=9000,
            purchase_amount=100000,
            purchase_shares=1111,
            profit=1000000,
            save_share_profit=0,
            save_share=0,
            is_current=False,
        )
    )

    record = Record(
        asset_id=asset.id,
        transactions_direction=Record.get_record_directoin_enum().SELL.value,
        transactions_date=datetime.combine(analysis_date, datetime.min.time()),
    )
    db.session.add(record)
    db.session.flush()

    db.session.add(
        GridTypeRecord(
            grid_type_id=grid_type.id,
            record_id=record.id,
        )
    )
    db.session.flush()
    db.session.commit()

    return {
        "analysis_date": analysis_date,
        "asset_id": asset.id,
        "grid_id": grid.id,
        "grid_type_id": grid_type.id,
    }


def _build_summary_frame(fund_name: str, fund_code: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "基金名称": fund_name,
                "基金代码": fund_code,
                "当日净值": 1.0,
                "单位成本": 0.95,
                "持有份额": 1000,
                "基金现值": 1000,
                "基金总申购": 950,
                "历史最大占用": 950,
                "基金持有成本": 950,
                "基金分红与赎回": 0,
                "换手率": 0.1,
                "基金收益总额": 50,
                "投资收益率": 0.0526,
                "内部收益率": 0.0526,
            },
            {
                "基金名称": "总计",
                "基金代码": fund_code,
                "当日净值": 1.0,
                "单位成本": 0.95,
                "持有份额": 1000,
                "基金现值": 1000,
                "基金总申购": 950,
                "历史最大占用": 950,
                "基金持有成本": 950,
                "基金分红与赎回": 0,
                "换手率": 0.1,
                "基金收益总额": 50,
                "投资收益率": 0.0526,
                "内部收益率": 0.0526,
            },
        ]
    )


def test_stage4_query_api_matrix_matches_current_scope():
    assert [row["capability"] for row in QUERY_API_COVERAGE_MATRIX] == [
        "资产查询",
        "交易记录查询",
        "分析结果查询",
        "系统查询入口 smoke",
        "查询读路径辅助链路",
    ]
    assert len(QUERY_API_COVERAGE_MATRIX) == 5
    assert all(row["manual"] in {"是", "否"} or row["manual"].startswith("是") for row in QUERY_API_COVERAGE_MATRIX)
    assert "&&" in FIXED_REGRESSION_COMMAND
    first_command, second_command = FIXED_REGRESSION_COMMAND.split(" && ", 1)
    assert first_command.startswith("pytest web/webtest/stage4/")
    assert "web/webtest/stage4" not in second_command
    assert second_command.startswith("pytest web/webtest/lite/")
    assert "tests/test_xalpha_databox_compat.py" in FIXED_REGRESSION_COMMAND


def test_stage4_asset_query_surface_is_covered_in_lite(lite_app):
    with lite_app.app_context():
        asset_id = _seed_asset_query_data()

    client = lite_app.test_client()
    list_response = client.get(
        "/api/asset/list/?page=1&pageSize=20&assetName=阶段4查询矩阵"
    )
    detail_response = client.get(f"/api/asset/{asset_id}")

    assert list_response.status_code == 200
    list_payload = list_response.get_json()
    assert list_payload["success"] is True
    assert list_payload["data"]["total"] == 1
    assert list_payload["data"]["items"][0]["assetName"] == "阶段4查询矩阵基金"
    assert list_payload["data"]["items"][0]["assetCode"] == "000001"

    assert detail_response.status_code == 200
    detail_payload = detail_response.get_json()
    assert detail_payload["success"] is True
    assert detail_payload["data"]["id"] == asset_id
    assert detail_payload["data"]["assetName"] == "阶段4查询矩阵基金"
    assert detail_payload["data"]["fundType"] == "STOCK_FUND"


def test_stage4_record_query_surface_is_covered_in_lite(lite_app):
    with lite_app.app_context():
        record_data = _seed_record_query_data()

    client = lite_app.test_client()
    create_response = client.post(
        "/api/record",
        json={
            "assetId": record_data["asset_id"],
            "transactionsShare": 300,
            "transactionsPrice": 13000,
            "transactionsFee": 30,
            "transactionsDirection": 1,
            "transactionsDate": "2024-01-03 10:00:00",
            "groupType": TradeReferenceGroupTypeEnum.GRID.value,
            "groupId": record_data["grid_type_one_id"],
        },
    )
    assert create_response.status_code == 200
    assert create_response.get_json()["success"] is True

    with lite_app.app_context():
        created_record = Record.query.order_by(Record.id.desc()).first()
        assert created_record is not None
        created_record_id = created_record.id

    update_response = client.put(
        "/api/record",
        json={
            "id": created_record_id,
            "transactionsPrice": 14000,
            "tradeReferences": [
                {
                    "groupType": TradeReferenceGroupTypeEnum.GRID.value,
                    "groupId": record_data["grid_type_two_id"],
                }
            ],
        },
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["success"] is True

    detail_response = client.get(f"/api/record/{created_record_id}")
    list_response = client.get(
        "/api/record_list?page=1&pageSize=10&assetName=阶段4查询矩阵记录资产&assetAlias=REC-001"
    )
    filtered_response = client.get(
        f"/api/record_list?page=1&pageSize=10&groupType={TradeReferenceGroupTypeEnum.GRID.value}&groupId={record_data['grid_type_two_id']}"
    )

    assert detail_response.status_code == 200
    detail_payload = detail_response.get_json()
    assert detail_payload["success"] is True
    assert detail_payload["data"]["assetId"] == record_data["asset_id"]
    assert detail_payload["data"]["assetName"] == "阶段4查询矩阵记录资产"
    assert detail_payload["data"]["transactionsPrice"] == "14000"

    assert list_response.status_code == 200
    list_payload = list_response.get_json()
    assert list_payload["success"] is True
    assert list_payload["data"]["total"] == 3
    assert list_payload["data"]["items"][0]["primaryAliasCode"] == "REC-001"
    assert list_payload["data"]["items"][0]["groupTypes"] == [
        TradeReferenceGroupTypeEnum.GRID.value
    ]

    assert filtered_response.status_code == 200
    filtered_payload = filtered_response.get_json()
    assert filtered_payload["success"] is True
    assert filtered_payload["data"]["total"] == 2
    assert created_record_id in [
        item["recordId"] for item in filtered_payload["data"]["items"]
    ]


def test_stage4_analysis_query_surface_is_covered_in_lite(lite_app):
    with lite_app.app_context():
        analysis_data = _seed_analysis_query_data()

    client = lite_app.test_client()
    with lite_app.app_context():
        mock_summary_frame = _build_summary_frame("阶段4查询矩阵分析基金", "000001")
        with patch(
            "web.services.analysis.transaction_analysis_service.webutils.is_trading_day"
        ) as mock_is_trading_day, patch(
            "web.services.analysis.transaction_analysis_service.databox.trade"
        ) as mock_trade, patch(
            "web.services.analysis.transaction_analysis_service.databox.summary"
        ) as mock_summary, patch(
            "web.services.analysis.transaction_analysis_service.databox.get_trade_fund_name"
        ) as mock_get_trade_fund_name, patch(
            "web.services.analysis.transaction_analysis_service.databox.remove_trade_cache"
        ) as mock_remove_cache:
            mock_is_trading_day.return_value = True
            mock_trade.return_value = 1
            mock_get_trade_fund_name.return_value = ("阶段4查询矩阵分析基金",)
            mock_summary.return_value = mock_summary_frame

            grid_type_service = GridTypeTransactionAnalysisService(
                grid_type_id=analysis_data["grid_type_id"]
            )
            grid_type_service.trade_analysis(
                start=analysis_data["analysis_date"],
                end=analysis_data["analysis_date"],
            )

            grid_service = GridTransactionAnalysisService(
                grid_id=analysis_data["grid_id"]
            )
            grid_service.trade_analysis(
                start=analysis_data["analysis_date"],
                end=analysis_data["analysis_date"],
            )

    grid_type_response = client.get(
        f"/api/analysis/grid-type-result/{analysis_data['grid_type_id']}"
    )
    grid_response = client.get(f"/api/analysis/grid-result/{analysis_data['grid_id']}")

    assert grid_type_response.status_code == 200
    grid_type_payload = grid_type_response.get_json()
    assert grid_type_payload["success"] is True
    assert grid_type_payload["data"]["gridTypeId"] == analysis_data["grid_type_id"]
    assert grid_type_payload["data"]["gridId"] == analysis_data["grid_id"]
    assert grid_type_payload["data"]["businessType"] == (
        GridTradeAnalysisData.get_business_type_enum().GRID_TYPE_ANALYSIS.value
    )

    assert grid_response.status_code == 200
    grid_payload = grid_response.get_json()
    assert grid_payload["success"] is True
    assert grid_payload["data"]["gridId"] == analysis_data["grid_id"]
    assert grid_payload["data"]["businessType"] == (
        GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value
    )

    with lite_app.app_context():
        assert GridTradeAnalysisData.query.count() == 2
        assert (
            GridTradeAnalysisData.query.filter_by(
                grid_type_id=analysis_data["grid_type_id"],
                business_type=GridTradeAnalysisData.get_business_type_enum().GRID_TYPE_ANALYSIS.value,
            ).one().grid_type_id
            == analysis_data["grid_type_id"]
        )
        assert (
            GridTradeAnalysisData.query.filter_by(
                grid_id=analysis_data["grid_id"],
                business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
            ).one().grid_id
            == analysis_data["grid_id"]
        )
        assert len(
            TradeAnalysisData.query.filter_by(asset_id=analysis_data["asset_id"]).order_by(
                TradeAnalysisData.record_date.asc()
            ).all()
        ) == 2


def test_stage4_system_smoke_surface_is_covered_in_lite(lite_app):
    client = lite_app.test_client()

    with patch(
        "web.databox.adapter.data.xa_data_adapter.xa.get_rt",
        return_value={
            "name": "Lite Smoke Asset",
            "current": 1.23,
            "market": None,
            "currency": None,
        },
    ) as mock_xalpha_get_rt:
        response = client.get("/token_test/result")

    assert response.status_code == 200
    assert response.get_json() == {
        "code": 20000,
        "data": True,
        "message": "成功",
        "success": True,
    }
    mock_xalpha_get_rt.assert_called_once_with(code="SH501018")
