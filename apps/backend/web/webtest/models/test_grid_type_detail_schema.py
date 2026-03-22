from web.models.grid.GridTypeDetail import GridTypeDetail, GridTypeDetailVOSchema


def test_grid_type_detail_vo_schema_accepts_numeric_gear():
    payload = {
        "id": 169,
        "gear": 0.8,
        "monitorType": 1,
        "triggerPurchasePrice": 14390,
        "purchasePrice": 14340,
        "purchaseShares": 1700,
        "triggerSellPrice": 15189,
        "sellPrice": 15240,
        "sellShares": 1700,
        "saveShare": 100,
        "isCurrent": False,
        "gridId": 14,
        "profit": 1530000,
        "gridTypeId": 15,
        "purchaseAmount": 24378000,
        "sellAmount": 24384000,
        "saveShareProfit": 6000,
        "actualSellShares": 1600,
    }

    detail = GridTypeDetailVOSchema().load(payload, unknown="EXCLUDE")

    assert isinstance(detail, GridTypeDetail)
    assert detail.gear == "0.8"
