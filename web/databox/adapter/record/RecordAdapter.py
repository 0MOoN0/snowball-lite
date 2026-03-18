from abc import ABC
from typing import List

import pandas as pd

from web.models.record.record import Record, RecordSchema


class RecordAdapter(ABC):

    def convert_record(self, records: List[Record]) -> pd.DataFrame:
        """
        转换交易记录，将数据库类型的交易记录转换为分析需要的格式
        Args:
            records: 数据库类型的交易记录

        Returns: 转换后的交易记录，默认是一个dataframe，包含['date', 'value', 'share', 'fee', 'asset_id']列
        """
        record_df = pd.DataFrame(RecordSchema().dump(records, many=True))
        # record_df[['transactions_date']] = pd.to_datetime(record_df['transactions_date']).apply(
        #     lambda x: x.strftime('%Y%m%d'))
        record_df['transactions_date'] = pd.to_datetime(record_df['transactions_date'])
        # 对日期进行升序排序
        record_df.sort_values(by=Record.transactions_date.key, inplace=True, ascending=True)
        record_df[['transactions_fee', 'transactions_price']] /= 1000
        enum_sell_value = Record.get_record_directoin_enum().SELL.value
        enum_transfer_out_value = Record.get_record_directoin_enum().TRANSFER_OUT.value
        enum_redemption_value = Record.get_record_directoin_enum().REDEMPTION.value
        negative_directions = [enum_sell_value, enum_transfer_out_value, enum_redemption_value]
        record_df.loc[record_df['transactions_direction'].isin(negative_directions), 'transactions_share'] = \
            record_df.loc[record_df['transactions_direction'].isin(negative_directions), 'transactions_share'].abs() * -1
        record_df.rename(
            columns={'transactions_date': 'date', 'transactions_price': 'value', 'transactions_share': 'share',
                     'transactions_fee': 'fee'}, inplace=True)
        return record_df[['date', 'value', 'share', 'fee', 'asset_id']]


class XaRecordAdapter(RecordAdapter):

    def __init__(self):
        pass
