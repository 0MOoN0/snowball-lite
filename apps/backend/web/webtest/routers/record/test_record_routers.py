import pytest
import json
from web.models import db
from web.models.asset.asset import Asset
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.record.record import Record
from web.models.record.trade_reference import TradeReference
from web.common.enum.business.record.trade_reference_enum import (
    TradeReferenceGroupTypeEnum,
)
from web.webtest.test_base import TestBaseWithRollback


class TestRecordRouters(TestBaseWithRollback):
    @pytest.fixture(autouse=True)
    def setup_data(self, rollback_session):
        # Create test data - Asset
        self.asset = Asset(asset_name="Test Asset", asset_code="TEST001")
        db.session.add(self.asset)
        db.session.flush()

        # Create Grid and GridType for validation test
        self.grid = Grid(grid_name="Test Grid", asset_id=self.asset.id)
        db.session.add(self.grid)
        db.session.flush()

        self.grid_type = GridType(
            type_name="Test Type", grid_id=self.grid.id, asset_id=self.asset.id
        )
        db.session.add(self.grid_type)
        db.session.commit()

        self.asset_id = self.asset.id
        self.grid_type_id = self.grid_type.id

    def test_crud_record_with_valid_grid(self, client):
        """
        测试交易记录的增删改查（关联有效的网格类型）
        """
        # 1. Create Record (POST) - 使用有效的网格类型ID
        create_data = {
            "assetId": self.asset_id,
            "groupType": TradeReferenceGroupTypeEnum.GRID.value,  # 网格类型
            "groupId": self.grid_type_id,  # 使用有效的网格类型ID
            "transactionsFee": 100,
            "transactionsShare": 1000,
            "transactionsDate": "2023-10-01 12:00:00",
            "transactionsPrice": 10000,
            "transactionsDirection": 1,
            "transactionsAmount": 10000000,
        }
        response = client.post("/api/record", json=create_data)
        assert response.status_code == 200, f"POST failed: {response.data}"
        result = json.loads(response.data)
        assert result["code"] == 20000
        assert result["success"] is True

        # Verify DB - Record
        record = Record.query.filter_by(transactions_fee=100).first()
        assert record is not None
        record_id = record.id

        # Verify DB - TradeReference
        trade_ref = TradeReference.query.filter_by(record_id=record_id).first()
        assert trade_ref is not None
        assert trade_ref.group_type == TradeReferenceGroupTypeEnum.GRID.value
        assert trade_ref.group_id == self.grid_type_id

        # 2. Get Record (GET)
        response = client.get(f"/api/record/{record_id}")
        assert response.status_code == 200, f"GET failed: {response.data}"
        result = json.loads(response.data)
        assert result["code"] == 20000
        assert result["data"]["transactionsFee"] == "100"

        # 3. Update Record (PUT)
        update_data = {
            "id": record_id,
            "transactionsFee": 200,
            "transactionsShare": 2000,
        }
        response = client.put("/api/record", json=update_data)
        assert response.status_code == 200, f"PUT failed: {response.data}"
        result = json.loads(response.data)
        assert result["code"] == 20000
        assert result["success"] is True

        # Verify Update
        db.session.expire(record)
        record = db.session.get(Record, record_id)
        assert record.transactions_fee == 200
        assert record.transactions_share == 2000

        # 4. Delete Record (DELETE)
        response = client.delete(f"/api/record/{record_id}")
        assert response.status_code == 200, f"DELETE failed: {response.data}"
        result = json.loads(response.data)
        assert result["code"] == 20000

        # Verify Delete - Record
        record = db.session.get(Record, record_id)
        assert record is None

        # Verify Delete - TradeReference also deleted
        trade_ref = TradeReference.query.filter_by(record_id=record_id).first()
        assert trade_ref is None

    def test_create_record_with_invalid_grid(self, client):
        """
        测试新增交易记录时关联不存在的网格类型（应返回错误）
        """
        create_data = {
            "assetId": self.asset_id,
            "groupType": TradeReferenceGroupTypeEnum.GRID.value,  # 网格类型
            "groupId": 999999,  # 不存在的网格类型ID
            "transactionsFee": 100,
            "transactionsShare": 1000,
            "transactionsDate": "2023-10-01 12:00:00",
            "transactionsPrice": 10000,
            "transactionsDirection": 1,
            "transactionsAmount": 10000000,
        }
        response = client.post("/api/record", json=create_data)
        assert response.status_code == 200, f"POST failed: {response.data}"
        result = json.loads(response.data)

        # 应返回失败
        assert result["success"] is False
        assert "网格类型不存在" in result["message"]

        # Verify DB - No Record created
        record = Record.query.filter_by(
            transactions_fee=100, transactions_share=1000
        ).first()
        assert record is None

    def test_create_record_without_group(self, client):
        """
        测试新增交易记录时不提供groupId（不创建关联，不需要网格校验）
        """
        create_data = {
            "assetId": self.asset_id,
            "transactionsFee": 50,
            "transactionsShare": 500,
            "transactionsDate": "2023-10-02 12:00:00",
            "transactionsPrice": 5000,
            "transactionsDirection": 0,
            "transactionsAmount": 2500000,
        }
        response = client.post("/api/record", json=create_data)
        assert response.status_code == 200, f"POST failed: {response.data}"
        result = json.loads(response.data)
        assert result["code"] == 20000

        # Verify DB - Record created
        record = Record.query.filter_by(transactions_fee=50).first()
        assert record is not None

        # Verify DB - No TradeReference created
        trade_ref = TradeReference.query.filter_by(record_id=record.id).first()
        assert trade_ref is None

    def test_create_record_with_other_group_type(self, client):
        """
        测试新增交易记录时使用其他分组类型（不进行网格校验）
        """
        create_data = {
            "assetId": self.asset_id,
            "groupType": TradeReferenceGroupTypeEnum.OTHER.value,  # 其他类型
            "groupId": 999999,  # 任意ID，不会校验
            "transactionsFee": 60,
            "transactionsShare": 600,
            "transactionsDate": "2023-10-03 12:00:00",
            "transactionsPrice": 6000,
            "transactionsDirection": 1,
            "transactionsAmount": 3600000,
        }
        response = client.post("/api/record", json=create_data)
        assert response.status_code == 200, f"POST failed: {response.data}"
        result = json.loads(response.data)
        assert result["code"] == 20000
        assert result["success"] is True

        # Verify DB - Record created
        record = Record.query.filter_by(transactions_fee=60).first()
        assert record is not None

        # Verify DB - TradeReference created with OTHER type
        trade_ref = TradeReference.query.filter_by(record_id=record.id).first()
        assert trade_ref is not None
        assert trade_ref.group_type == TradeReferenceGroupTypeEnum.OTHER.value

    def test_get_record_detail_with_references(self, client):
        """
        测试获取交易记录详情（包含关联信息）
        """
        # 1. Create Record with Association
        create_data = {
            "assetId": self.asset_id,
            "groupType": TradeReferenceGroupTypeEnum.GRID.value,
            "groupId": self.grid_type_id,
            "transactionsFee": 100,
            "transactionsShare": 1000,
            "transactionsDate": "2023-10-01 12:00:00",
            "transactionsPrice": 10000,
            "transactionsDirection": 1,
        }
        response = client.post("/api/record", json=create_data)
        assert response.status_code == 200
        # 假设创建成功，获取 ID
        # 由于POST不返回ID（只返回成功消息），我们需要从DB查询
        record = (
            Record.query.filter_by(transactions_fee=100)
            .order_by(Record.id.desc())
            .first()
        )
        record_id = record.id

        # 2. Get Detail
        response = client.get(f"/api/record/{record_id}")
        assert response.status_code == 200
        result = json.loads(response.data)

        assert result["code"] == 20000
        data = result["data"]
        assert data["recordId"] == record_id

        # Check Trade References
        assert "tradeReferences" in data
        assert len(data["tradeReferences"]) == 1
        ref = data["tradeReferences"][0]
        assert ref["groupType"] == TradeReferenceGroupTypeEnum.GRID.value
        assert ref["groupId"] == self.grid_type_id

        # Check Group Types Summary
        assert "groupTypes" in data
        assert TradeReferenceGroupTypeEnum.GRID.value in data["groupTypes"]

    def test_update_record_with_references_replace(self, client):
        """
        测试更新交易记录的同时替换关联关系
        """
        # 1. Create Record with Initial Association (Type 1)
        create_data = {
            "assetId": self.asset_id,
            "groupType": TradeReferenceGroupTypeEnum.GRID.value,
            "groupId": self.grid_type_id,
            "transactionsFee": 100,
            "transactionsShare": 1000,
            "transactionsDate": "2023-10-01 12:00:00",
            "transactionsPrice": 10000,
            "transactionsDirection": 1,
        }
        client.post("/api/record", json=create_data)
        record = (
            Record.query.filter_by(transactions_fee=100)
            .order_by(Record.id.desc())
            .first()
        )
        record_id = record.id

        # 2. Update Record: Change to Type 2 (Mock another grid type id, assuming validation passes or we create one)
        # Create another GridType for testing
        grid_type_2 = GridType(
            type_name="Test Type 2", grid_id=self.grid.id, asset_id=self.asset.id
        )
        db.session.add(grid_type_2)
        db.session.flush()  # flush to get ID

        update_data = {
            "id": record_id,
            "transactionsFee": 150,  # Update basic field
            "tradeReferences": [
                {
                    "groupType": TradeReferenceGroupTypeEnum.GRID.value,
                    "groupId": grid_type_2.id,
                }
            ],
        }

        response = client.put("/api/record", json=update_data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["success"] is True

        # 3. Verify DB
        db.session.expire(record)
        updated_record = db.session.get(Record, record_id)
        assert updated_record.transactions_fee == 150

        refs = TradeReference.query.filter_by(record_id=record_id).all()
        assert len(refs) == 1
        assert refs[0].group_id == grid_type_2.id
