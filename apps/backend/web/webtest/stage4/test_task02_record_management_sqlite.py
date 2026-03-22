from __future__ import annotations

from datetime import datetime

import pytest

from web.common.enum.business.record.trade_reference_enum import (
    TradeReferenceGroupTypeEnum,
)
from web.models import db
from web.models.asset.asset import Asset
from web.models.asset.asset_alias import AssetAlias
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.record.record import Record
from web.models.record.trade_reference import TradeReference
from web.webtest.test_base import TestBaseLiteWithRollback


pytestmark = [pytest.mark.local, pytest.mark.integration]


def _seed_record_asset(asset_name: str, alias_symbol: str) -> Asset:
    asset = Asset(
        asset_name=asset_name,
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
            provider_symbol=alias_symbol,
            provider_name="manual",
            is_primary=True,
            status=1,
        )
    )
    db.session.flush()
    return asset


class TestTask02RecordManagementSQLite(TestBaseLiteWithRollback):
    @pytest.fixture(autouse=True)
    def setup_data(self, lite_rollback_session):
        self.asset = _seed_record_asset("阶段4记录资产", "REC-001")
        self.grid = Grid(grid_name="阶段4网格", asset_id=self.asset.id)
        lite_rollback_session.add(self.grid)
        lite_rollback_session.flush()

        self.grid_type_one = GridType(
            grid_id=self.grid.id,
            asset_id=self.asset.id,
            type_name="阶段4网格类型一",
            grid_type_status=0,
        )
        self.grid_type_two = GridType(
            grid_id=self.grid.id,
            asset_id=self.asset.id,
            type_name="阶段4网格类型二",
            grid_type_status=0,
        )
        lite_rollback_session.add_all([self.grid_type_one, self.grid_type_two])
        lite_rollback_session.flush()

        self.record_one = Record(
            asset_id=self.asset.id,
            transactions_date=datetime(2024, 1, 1, 10, 0, 0),
            transactions_fee=10,
            transactions_share=100,
            transactions_price=10000,
            transactions_direction=1,
            transactions_amount=1000000,
        )
        self.record_two = Record(
            asset_id=self.asset.id,
            transactions_date=datetime(2024, 1, 2, 10, 0, 0),
            transactions_fee=20,
            transactions_share=200,
            transactions_price=12000,
            transactions_direction=0,
            transactions_amount=2400000,
        )
        lite_rollback_session.add_all([self.record_one, self.record_two])
        lite_rollback_session.flush()

        self.ref_one = TradeReference(
            record_id=self.record_one.id,
            group_type=TradeReferenceGroupTypeEnum.GRID.value,
            group_id=self.grid_type_one.id,
        )
        self.ref_two = TradeReference(
            record_id=self.record_two.id,
            group_type=TradeReferenceGroupTypeEnum.GRID.value,
            group_id=self.grid_type_two.id,
        )
        lite_rollback_session.add_all([self.ref_one, self.ref_two])
        lite_rollback_session.commit()

    def test_record_lite_list_update_reference_closed_loop(self, lite_webtest_client):
        create_response = lite_webtest_client.post(
            "/api/record",
            json={
                "assetId": self.asset.id,
                "transactionsShare": 300,
                "transactionsPrice": 13000,
                "transactionsFee": 30,
                "transactionsDirection": 1,
                "transactionsDate": "2024-01-03 10:00:00",
                "groupType": TradeReferenceGroupTypeEnum.GRID.value,
                "groupId": self.grid_type_one.id,
            },
        )

        assert create_response.status_code == 200
        assert create_response.get_json()["success"] is True

        created_record = Record.query.order_by(Record.id.desc()).first()
        assert created_record is not None

        detail_response = lite_webtest_client.get(f"/api/record/{created_record.id}")
        assert detail_response.status_code == 200
        detail_payload = detail_response.get_json()
        assert detail_payload["success"] is True
        assert detail_payload["data"]["assetId"] == self.asset.id
        assert detail_payload["data"]["assetName"] == "阶段4记录资产"

        list_response = lite_webtest_client.get(
            "/api/record_list?page=1&pageSize=10&assetName=阶段4记录资产&assetAlias=REC-001"
        )
        assert list_response.status_code == 200
        list_payload = list_response.get_json()
        assert list_payload["success"] is True
        assert list_payload["data"]["total"] == 3
        assert list_payload["data"]["items"][0]["recordId"] == created_record.id
        assert list_payload["data"]["items"][0]["primaryAliasCode"] == "REC-001"
        assert list_payload["data"]["items"][0]["groupTypes"] == [
            TradeReferenceGroupTypeEnum.GRID.value
        ]

        update_response = lite_webtest_client.put(
            "/api/record",
            json={
                "id": created_record.id,
                "transactionsPrice": 14000,
                "tradeReferences": [
                    {
                        "groupType": TradeReferenceGroupTypeEnum.GRID.value,
                        "groupId": self.grid_type_two.id,
                    }
                ],
            },
        )
        assert update_response.status_code == 200
        assert update_response.get_json()["success"] is True

        refreshed_detail = lite_webtest_client.get(f"/api/record/{created_record.id}")
        assert refreshed_detail.status_code == 200
        refreshed_payload = refreshed_detail.get_json()
        assert refreshed_payload["success"] is True
        assert refreshed_payload["data"]["transactionsPrice"] == "14000"
        assert refreshed_payload["data"]["tradeReferences"][0]["groupId"] == self.grid_type_two.id

        filtered_response = lite_webtest_client.get(
            f"/api/record_list?page=1&pageSize=10&groupType={TradeReferenceGroupTypeEnum.GRID.value}&groupId={self.grid_type_two.id}"
        )
        assert filtered_response.status_code == 200
        filtered_payload = filtered_response.get_json()
        assert filtered_payload["success"] is True
        assert filtered_payload["data"]["total"] == 2
        assert created_record.id in [item["recordId"] for item in filtered_payload["data"]["items"]]
