from pprint import pprint

import pandas as pd
from sqlalchemy import and_

from web.models.record.record import Record, RecordSchema
from web.webtest.TestModelsClass import TestBasicModels


class RecordTestBasicModels(TestBasicModels):

    def test_record(self):
        record_list = Record.query.filter(and_(Record.strategy_type == Record.get_strategy_key_enum().GRID.value,
                                               Record.strategy_key == 1)).all()
        record_list_dict = RecordSchema().dump(record_list, many=True)
        df = pd.DataFrame(record_list_dict)
        pprint(df)
