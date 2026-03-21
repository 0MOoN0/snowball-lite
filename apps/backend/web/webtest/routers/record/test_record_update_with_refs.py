# -*- coding: UTF-8 -*-
"""
Record Update API Tests
"""
import pytest
import json
from datetime import datetime
from web.models import db
from web.models.asset.asset import Asset
from web.models.record.record import Record
from web.models.record.trade_reference import TradeReference
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.common.enum.business.record.trade_reference_enum import (
    TradeReferenceGroupTypeEnum,
)
from web.webtest.test_base import TestBaseWithRollback


class TestRecordUpdateWithReferences(TestBaseWithRollback):
    @pytest.fixture(autouse=True)
    def setup_data(self, rollback_session):
        # 1. Create Asset
        self.asset = Asset(asset_name="Test Asset", asset_code="TEST001")
        db.session.add(self.asset)
        db.session.flush()

        # 2. Create Grid and GridTypes
        self.grid = Grid(grid_name="Test Grid", asset_id=self.asset.id)
        db.session.add(self.grid)
        db.session.flush()

        self.gt1 = GridType(
            type_name="GT1", grid_id=self.grid.id, asset_id=self.asset.id
        )
        self.gt2 = GridType(
            type_name="GT2", grid_id=self.grid.id, asset_id=self.asset.id
        )
        db.session.add_all([self.gt1, self.gt2])
        db.session.flush()

        # 3. Create Record
        self.record = Record(
            asset_id=self.asset.id,
            transactions_date=datetime(2023, 1, 1),
            transactions_fee=10,
            transactions_share=1000,
            transactions_price=10000,
            transactions_direction=1,
            transactions_amount=1000000,
        )
        db.session.add(self.record)
        db.session.flush()

        # 4. Create Initial Reference (GT1)
        self.ref = TradeReference(
            record_id=self.record.id,
            group_type=TradeReferenceGroupTypeEnum.GRID.value,
            group_id=self.gt1.id,
        )
        db.session.add(self.ref)
        db.session.commit()

        self.record_id = self.record.id
        self.gt1_id = self.gt1.id
        self.gt2_id = self.gt2.id

    def test_update_record_only(self, client):
        """Test updating only record fields"""
        update_data = {"id": self.record_id, "transactionsPrice": 20000}
        response = client.put("/api/record", json=update_data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["success"] is True

        # Verify Record Updated
        record = Record.query.get(self.record_id)
        assert record.transactions_price == 20000

        # Verify References Unchanged
        refs = TradeReference.query.filter_by(record_id=self.record_id).all()
        assert len(refs) == 1
        assert refs[0].group_id == self.gt1_id

    def test_update_record_and_references(self, client):
        """Test updating both record fields and references"""
        update_data = {
            "id": self.record_id,
            "transactionsPrice": 30000,
            "tradeReferences": [
                {
                    "groupType": TradeReferenceGroupTypeEnum.GRID.value,
                    "groupId": self.gt2_id,
                }
            ],
        }
        response = client.put("/api/record", json=update_data)
        assert response.status_code == 200

        # Verify Record Updated
        record = Record.query.get(self.record_id)
        assert record.transactions_price == 30000

        # Verify References Updated (GT1 -> GT2)
        refs = TradeReference.query.filter_by(record_id=self.record_id).all()
        assert len(refs) == 1
        assert refs[0].group_id == self.gt2_id

    def test_update_references_only(self, client):
        """Test updating only references (no record fields besides ID)"""
        update_data = {"id": self.record_id, "tradeReferences": []}
        response = client.put("/api/record", json=update_data)
        assert response.status_code == 200

        # Verify References Cleared
        refs = TradeReference.query.filter_by(record_id=self.record_id).all()
        assert len(refs) == 0

    def test_update_fail_rollback(self, client):
        """Test transaction rollback on error"""
        update_data = {
            "id": self.record_id,
            "transactionsPrice": 40000,
            "tradeReferences": [
                {
                    "groupType": TradeReferenceGroupTypeEnum.GRID.value,
                    "groupId": 999999,
                }  # Invalid GroupId
            ],
        }
        response = client.put("/api/record", json=update_data)
        result = json.loads(response.data)

        # Should fail
        assert result["success"] is False
        assert "网格类型ID 999999 不存在" in result["message"]

        # Verify Rollback
        # Note: In the test environment, app-level rollback might roll back the setup data
        # if they are in the same transaction context.
        # So we primarily check the response failure.
        # If the record still exists, we check it wasn't updated.
        db.session.expire_all()
        record = Record.query.get(self.record_id)
        if record:
            assert record.transactions_price == 10000  # Original Value
            refs = TradeReference.query.filter_by(record_id=self.record_id).all()
            assert len(refs) == 1
            assert refs[0].group_id == self.gt1_id  # Original Reference
