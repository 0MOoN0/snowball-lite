from sqlalchemy import func, and_

from web.models import db
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.record.record import Record
from web.webtest.TestModelsClass import TestBasicModels


class GridTestBasicModels(TestBasicModels):

    def test_select(self):
        asset_id = db.session.query(Grid.asset_id).join(GridType, Grid.id == GridType.grid_id) \
            .filter(GridType.id == 1).first()
        print(asset_id)

    def test_grid_record(self):
        sell_enum_value = Record.get_record_directoin_enum().SELL.value
        result = db.session.query(func.count(Record.transactions_direction).label('sell_times')) \
            .join(GridTypeRecord, GridTypeRecord.record_id == Record.id, isouter=True) \
            .filter(and_(GridTypeRecord.grid_type_id == 1, Record.transactions_direction == sell_enum_value)) \
            .all()
        print(result)
