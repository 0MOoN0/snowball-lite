from __future__ import annotations

import pytest

from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.notice.Notification import Notification
from web.models.record.record import Record
from web.models.asset.asset import Asset
from web.webtest.test_base import TestBaseLiteWithRollback


pytestmark = [pytest.mark.local, pytest.mark.integration]


class TestLiteNotificationDetailRouter(TestBaseLiteWithRollback):
    @pytest.fixture(autouse=True)
    def setup_data(self, lite_rollback_session):
        self.asset = Asset(
            asset_code="000001",
            asset_name="通知确认资产",
            asset_type=1,
            currency=1,
            market=1,
            asset_status=0,
        )
        lite_rollback_session.add(self.asset)
        lite_rollback_session.flush()

        self.grid = Grid(
            grid_name="通知确认网格",
            asset_id=self.asset.id,
            grid_status=Grid.get_status_enum().ENABLE.value,
        )
        lite_rollback_session.add(self.grid)
        lite_rollback_session.flush()

        self.grid_type = GridType(
            grid_id=self.grid.id,
            grid_type_status=0,
            type_name="通知确认网格类型",
            asset_id=self.asset.id,
        )
        lite_rollback_session.add(self.grid_type)
        lite_rollback_session.flush()

        self.grid_type_detail = GridTypeDetail(
            grid_type_id=self.grid_type.id,
            grid_id=self.grid.id,
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
        lite_rollback_session.add(self.grid_type_detail)
        lite_rollback_session.flush()

        self.notification = Notification(
            business_type=Notification.get_business_type_enum().GRID_TRADE.value,
            notice_type=Notification.get_notice_type_enum().CONFIRM_MESSAGE.value,
            notice_status=Notification.get_notice_status_enum().NOT_READ.value,
            title="待确认通知",
        )
        lite_rollback_session.add(self.notification)
        lite_rollback_session.flush()

    def test_put_notification_confirm_persists_trade_record_in_sqlite(
        self, lite_webtest_client
    ):
        response = lite_webtest_client.put(
            f"/api/notification/{self.notification.id}",
            json={
                "confirmData": [
                    {
                        "tradeRecord": [
                            {
                                str(self.grid_type_detail.id): {
                                    "recordId": 999,
                                    "transactionsFee": "0.1",
                                    "transactionsShare": "100",
                                    "transactionsDate": "2026-03-22 16:01:44",
                                    "transactionsPrice": "50.123",
                                    "transactionsDirection": 1,
                                    "transactionsAmount": "100.0",
                                }
                            }
                        ]
                    }
                ]
            },
        )

        assert response.status_code == 200
        payload = response.get_json()
        assert payload["success"] is True

        saved_notification = Notification.query.get(self.notification.id)
        saved_record = Record.query.one()
        saved_link = GridTypeRecord.query.one()
        saved_detail = GridTypeDetail.query.get(self.grid_type_detail.id)

        assert (
            saved_notification.notice_status
            == Notification.get_notice_status_enum().PROCESSED.value
        )
        assert saved_record.asset_id == self.asset.id
        assert saved_record.transactions_fee == 100
        assert saved_record.transactions_share == 100
        assert saved_record.transactions_price == 50123
        assert saved_record.transactions_amount == 100000
        assert saved_record.transactions_direction == 1
        assert saved_link.grid_type_id == self.grid_type.id
        assert saved_link.record_id == saved_record.id
        assert (
            saved_detail.monitor_type
            == GridTypeDetail.get_monitor_type_enum().BUY.value
        )
