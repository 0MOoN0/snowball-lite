from web.models import db
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.webtest.TestModelsClass import TestBasicModels


class GridTypeTestBasicModels(TestBasicModels):
    def test_select_grid_type_by_assetid(self):
        result = db.session.query(GridType.id).join(Grid, Grid.id == GridType.grid_id,
                                                    isouter=True).filter(
            Grid.asset_id == 12).all()
        ids = [grid.id for grid in result]
        print(result)
