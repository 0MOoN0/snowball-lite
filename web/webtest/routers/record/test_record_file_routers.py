import pytest
from datetime import datetime
import pandas as pd
from io import BytesIO

from web.models import db
from web.models.asset.asset import Asset
from web.models.record.record import Record
from web.models.asset.asset_alias import AssetAlias
from web.webtest.test_base import TestBaseWithRollback


class TestRecordFileRouter(TestBaseWithRollback):

    @pytest.fixture(autouse=True)
    def setup_data(self, rollback_session):
        # 1. Create Asset
        self.asset = Asset(asset_name="Test File Asset", asset_code="FILE001")
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
        rollback_session.flush()

        # 2. Create Records
        self.record_1 = Record(
            asset_id=self.asset.id,
            transactions_date=datetime(2023, 1, 1, 10, 0, 0),
            transactions_fee=10,  # 0.01 Yuan
            transactions_share=100,
            transactions_price=10000,  # 10.00 Yuan
            transactions_direction=1,  # Buy
            transactions_amount=1000000,  # 1000.00 Yuan
        )

        rollback_session.add(self.record_1)
        rollback_session.flush()

    def test_export_records(self, client):
        """测试导出交易记录"""
        response = client.get("/api/record_file/export")

        assert response.status_code == 200
        assert (
            response.headers["Content-Type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        # assert "attachment; filename*=UTF-8''" in response.headers["Content-Disposition"] or "filename=" in response.headers["Content-Disposition"]

        # Read the excel file
        content = response.data
        df = pd.read_excel(BytesIO(content))

        assert len(df) >= 1

        # Check columns
        expected_columns = [
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
        for col in expected_columns:
            assert col in df.columns

        # Check data
        # Find our record by asset name and date
        # Note: Transaction date comparison might need adjustment depending on how pandas reads excel dates
        # Here we just check if we can find a row with matching asset name and amount
        record_rows = df[df["资产名称"] == "Test File Asset"]
        assert len(record_rows) >= 1

        # Get the first matching row (assuming it's ours or similar enough)
        record_row = record_rows.iloc[0]
        assert record_row["资产名称"] == "Test File Asset"
        assert record_row["交易方向"] == "买入"
        assert record_row["交易价格(元)"] == 10.00
        assert record_row["交易金额(元)"] == 1000.00
        assert record_row["交易费用(元)"] == 0.01

    def test_check_export_records(self, client):
        """测试导出前检查"""
        # Add another record
        record_2 = Record(
            asset_id=self.asset.id,
            transactions_date=datetime(2023, 1, 2, 10, 0, 0),
            transactions_fee=20,
            transactions_share=200,
            transactions_price=20000,
            transactions_direction=0,  # Sell
            transactions_amount=4000000,
        )
        db.session.add(record_2)
        db.session.commit()

        # 1. Check all
        response = client.get("/api/record_file/export/check")
        assert response.status_code == 200
        data = response.json
        assert data["success"] is True
        # We have at least 2 records (record_1 and record_2), maybe more from other tests if not cleaned properly?
        # But TestBaseWithRollback should handle it.
        # Actually setup_data runs for each test.
        # So here we should have exactly 2 records.
        assert data["data"]["count"] == 2

        # 2. Check with filter
        response = client.get("/api/record_file/export/check?transactionsDirection=0")
        assert response.status_code == 200
        data = response.json
        assert data["success"] is True
        assert data["data"]["count"] == 1

    def test_export_records_with_filter(self, client):
        """测试带筛选条件的导出"""
        # Add another record
        record_2 = Record(
            asset_id=self.asset.id,
            transactions_date=datetime(2023, 1, 2, 10, 0, 0),
            transactions_fee=20,
            transactions_share=200,
            transactions_price=20000,
            transactions_direction=0,  # Sell
            transactions_amount=4000000,
        )
        db.session.add(record_2)
        db.session.commit()

        # Filter by direction = 0 (Sell)
        response = client.get("/api/record_file/export?transactionsDirection=0")

        assert response.status_code == 200
        df = pd.read_excel(BytesIO(response.data))

        # Should only contain record_2
        assert len(df) == 1
        assert df.iloc[0]["交易方向"] == "卖出"
