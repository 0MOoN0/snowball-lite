import pytest
import json
from datetime import datetime
from web.models import db
from web.models.asset.asset import Asset
from web.models.record.record import Record
from web.models.record.trade_reference import TradeReference
from web.common.enum.business.record.trade_reference_enum import (
    TradeReferenceGroupTypeEnum,
)
from web.webtest.test_base import TestBaseWithRollback

from web.models.asset.asset_alias import AssetAlias


class TestRecordListRouter(TestBaseWithRollback):

    @pytest.fixture(autouse=True)
    def setup_data(self, rollback_session):
        # 1. Create Asset
        self.asset = Asset(asset_name="Test List Asset", asset_code="LIST001")
        rollback_session.add(self.asset)
        rollback_session.flush()

        # 1.1 Create Asset Alias (Primary)
        self.alias_primary = AssetAlias(
            asset_id=self.asset.id,
            provider_code="yahoo",
            provider_symbol="AAPL",
            provider_name="Apple Inc.",
            is_primary=1,
            status=1,
        )
        rollback_session.add(self.alias_primary)

        # 1.2 Create Asset Alias (Secondary) for alias search test
        self.alias_secondary = AssetAlias(
            asset_id=self.asset.id,
            provider_code="google",
            provider_symbol="GOOGL",
            provider_name="Alphabet Inc.",
            is_primary=0,
            status=1,
        )
        rollback_session.add(self.alias_secondary)
        rollback_session.flush()

        # 2. Create Records
        # Record 1: 关联到 group_id=1 (网格类型)
        self.record_1 = Record(
            asset_id=self.asset.id,
            transactions_date=datetime(2023, 1, 1, 10, 0, 0),
            transactions_fee=10,
            transactions_share=100,
            transactions_price=10000,
            transactions_direction=1,
            transactions_amount=1000000,
        )

        # Record 2: 关联到 group_id=2 (网格类型)
        self.record_2 = Record(
            asset_id=self.asset.id,
            transactions_date=datetime(2023, 1, 2, 10, 0, 0),
            transactions_fee=20,
            transactions_share=200,
            transactions_price=20000,
            transactions_direction=0,
            transactions_amount=4000000,
        )

        # Record 3: 关联到 group_id=1 (网格类型)
        self.record_3 = Record(
            asset_id=self.asset.id,
            transactions_date=datetime(2023, 1, 3, 10, 0, 0),
            transactions_fee=30,
            transactions_share=300,
            transactions_price=30000,
            transactions_direction=1,
            transactions_amount=9000000,
        )

        rollback_session.add_all([self.record_1, self.record_2, self.record_3])
        rollback_session.flush()

        # 3. Create TradeReference Associations
        # group_type=1 表示网格类型
        self.group_id_1 = 1001  # 模拟的业务对象ID
        self.group_id_2 = 1002

        ref_1 = TradeReference(
            record_id=self.record_1.id,
            group_type=TradeReferenceGroupTypeEnum.GRID.value,
            group_id=self.group_id_1,
        )
        ref_2 = TradeReference(
            record_id=self.record_2.id,
            group_type=TradeReferenceGroupTypeEnum.GRID.value,
            group_id=self.group_id_2,
        )
        ref_3 = TradeReference(
            record_id=self.record_3.id,
            group_type=TradeReferenceGroupTypeEnum.GRID.value,
            group_id=self.group_id_1,
        )

        rollback_session.add_all([ref_1, ref_2, ref_3])
        rollback_session.commit()

    def test_get_record_list_success(self, client):
        """测试获取交易记录列表成功"""
        response = client.get("/api/record_list?page=1&pageSize=10")

        assert response.status_code == 200
        result = json.loads(response.data)

        assert result["code"] == 20000
        assert result["success"] is True
        assert result["data"]["total"] >= 3
        items = result["data"]["items"]
        assert len(items) >= 3

        # Verify Alias Fields
        first_item = items[0]
        # In this test case (no filter), we get 3 records.
        # record_3 (latest) -> group_id_1 -> primary alias AAPL
        # record_2 (middle) -> group_id_2 -> primary alias AAPL
        # record_1 (oldest) -> group_id_1 -> primary alias AAPL
        # All records belong to self.asset, which has primary alias AAPL.

        # We need to find one record that belongs to self.asset to verify
        for item in items:
            if item["assetId"] == self.asset.id:
                assert item["primaryAliasCode"] == "AAPL"
                assert item["primaryProviderName"] == "Apple Inc."
                break

        # Verify sorting (descending by date)
        # Note: other tests might add records, so we check relative order if we can,
        # or just check if our created records are present.
        # Since we are in a rollback session, other tests shouldn't interfere unless running in parallel on same DB (which pytest-xdist might do but we have scoped session).
        # Let's check if record_3 (newest) comes before record_1 (oldest) among the ones we created.

        ids = [item["recordId"] for item in items]
        assert self.record_3.id in ids
        assert self.record_2.id in ids
        assert self.record_1.id in ids

        # Find indices
        idx_3 = ids.index(self.record_3.id)
        idx_2 = ids.index(self.record_2.id)
        idx_1 = ids.index(self.record_1.id)

        # Date 3 > Date 2 > Date 1, so Order should be 3, 2, 1
        assert idx_3 < idx_2
        assert idx_2 < idx_1

    def test_get_record_list_with_group_filter(self, client):
        """
        测试按分组类型和业务对象ID筛选交易记录
        """
        # Filter by groupType=1, groupId=group_id_1 (Should have Record 1 and 3)
        response = client.get(
            f"/api/record_list?page=1&pageSize=10&groupType={TradeReferenceGroupTypeEnum.GRID.value}&groupId={self.group_id_1}"
        )

        assert response.status_code == 200
        result = json.loads(response.data)

        items = result["data"]["items"]
        ids = [item["recordId"] for item in items]

        assert self.record_1.id in ids
        assert self.record_3.id in ids
        assert self.record_2.id not in ids  # Record 2 belongs to group_id_2

    def test_get_record_list_with_alias_filter(self, client):
        """
        测试按资产别名筛选交易记录
        """
        # Filter by assetAlias="GOOGL" (Secondary alias of our asset)
        # Should find records associated with self.asset
        response = client.get(f"/api/record_list?page=1&pageSize=10&assetAlias=GOOGL")

        assert response.status_code == 200
        result = json.loads(response.data)

        items = result["data"]["items"]
        ids = [item["recordId"] for item in items]

        assert self.record_1.id in ids
        assert self.record_2.id in ids
        assert self.record_3.id in ids

    def test_get_record_list_pagination(self, client):
        """
        测试分页功能
        """
        # Page 1, Size 1
        response = client.get("/api/record_list?page=1&pageSize=1")
        result = json.loads(response.data)
        items = result["data"]["items"]
        assert len(items) == 1
        # Should be the latest one (Record 3)
        # Note: This assumes no other records created by other tests are newer.
        # Ideally, we should rely on what we created.

        # Page 2, Size 1
        response = client.get("/api/record_list?page=2&pageSize=1")
        result = json.loads(response.data)
        items = result["data"]["items"]
        assert len(items) == 1

    def test_get_record_list_empty(self, client):
        """
        测试查询无结果的情况
        """
        # Use a non-existent groupId
        response = client.get(
            f"/api/record_list?page=1&pageSize=10&groupType={TradeReferenceGroupTypeEnum.GRID.value}&groupId=999999"
        )

        assert response.status_code == 200
        result = json.loads(response.data)

        assert result["data"]["total"] == 0
        assert len(result["data"]["items"]) == 0

    def test_get_record_list_missing_params(self, client):
        """
        测试缺少必填参数 (page, pageSize)
        """
        # Missing pageSize
        response = client.get("/api/record_list?page=1")
        # Marshmallow schema required=True usually raises ValidationError which might be handled
        # by a global error handler to return 400 or a specific error format.
        # The project rules say: ValidationError/BadRequest in api_factory.py re-throws,
        # global handler returns R.fail.

        result = json.loads(response.data)
        # Expecting failure
        assert result["success"] is False
        # Message usually contains field name
        assert (
            "pageSize" in str(result)
            or "每页显示的记录条数" in str(result)
            or "Missing data for required field" in str(result)
        )
