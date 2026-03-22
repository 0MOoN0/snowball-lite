from typing import List

from pandas import DataFrame

from web.decorator import singleton
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail, GridTypeDetailDomainSchema


@singleton
class GridService:
    def to_judge_gen_transaction(self, grid_type: GridType, daily_data: AssetFundDailyData,
                                 grid_type_detail: List[GridTypeDetail]) -> List:
        """
        方法内容：判断是否生成交易记录
        Args:
            grid_type (GridType):   网格类型
            daily_data (AssetFundDailyData):    当天数据
            grid_type_detail (List[GridTypeDetail]):   网格类型详情

        Returns:
            List:   可能发生交易的网格类型详情ID列表，如果没有产生交易记录，返回空列表
        """
        if len(grid_type_detail) == 0:
            return []
        result = []
        # 获取当天数据
        grid_detail_df = DataFrame(GridTypeDetailDomainSchema().dump(grid_type_detail, many=True))
        grid_detail_df.sort_values('gear', inplace=True, ascending=False)
        # 获取当前监控的详情数据
        cur = grid_detail_df[grid_detail_df[GridTypeDetail.is_current.key] == 1].to_dict(orient='record')
        if len(cur) == 0:
            return result
        cur_detail: GridTypeDetail = GridTypeDetailDomainSchema().load(cur, many=True)[0]
        # 如果当天数据最大值大于监控数据的触发卖出价，并且网格类型不是只买不卖
        if daily_data.f_high >= cur_detail.trigger_sell_price and \
                grid_type.grid_type_status != grid_type.get_grid_status_enum().BUY_ONLY:
            # 可能发生卖出交易，筛选所有大于当前监控档位，并且卖出触发价小于当天最大值的数据列、网格类型类型为卖出
            sell_df = grid_detail_df[
                (grid_detail_df[GridTypeDetail.gear.key] >= cur_detail.gear) &
                # 可能发生交易的网格类型的触发卖出价应该是要小于当天的最大值，否则不会发生交易，买入同理
                (grid_detail_df[GridTypeDetail.trigger_sell_price.key] < daily_data.f_high) &
                (grid_detail_df[GridTypeDetail.monitor_type.key] == GridTypeDetail.get_monitor_type_enum().SELL)]
            # 如果存在数据，说明可能卖出
            if len(sell_df) > 0:
                result.extend(sell_df['id'].unique())
        # 如果当天数据最小值小于监控数据的触发买入价，并且网格类型不是只卖不买
        if daily_data.f_low <= cur_detail.trigger_purchase_price and \
                grid_type.grid_type_status != grid_type.get_grid_status_enum().SELL_ONLY:
            # 可能发生买入交易，筛选所有小于当前监控档位，并且买入触发价大于当天最小值的数据列、网格类型类型为买入
            buy_df = grid_detail_df[
                (grid_detail_df[GridTypeDetail.gear.key] <= cur_detail.gear) &
                (grid_detail_df[GridTypeDetail.trigger_purchase_price.key] > daily_data.f_low) &
                (grid_detail_df[GridTypeDetail.monitor_type.key] == GridTypeDetail.get_monitor_type_enum().BUY)]
            # 如果存在数据，说明可能买入
            if len(buy_df) > 0:
                result.extend(buy_df['id'].unique())
        return result

    def to_judge_monitor_change(self, today_daily_data: AssetFundDailyData, grid_type_detail: List[GridTypeDetail]) -> List:
        """
        方法内容：判断是否需要更换监控档位
        Args:
            today_daily_data (AssetFundDailyData):    当天数据
            grid_type_detail (List[GridTypeDetail]):   网格类型详情
        Returns:
            List:   需要更换监控档位的网格类型详情ID列表，如果没有产生交易记录，返回空列表
        """
        # 根据当前数据的收盘点位判断应该处于哪个档位
        detail_df = DataFrame(GridTypeDetailDomainSchema().dump(grid_type_detail, many=True))
        detail_df.sort_values(GridTypeDetail.gear.key, inplace=True, ascending=False)
        # 获取当前监控的详情数据
        cur = detail_df[detail_df[GridTypeDetail.is_current.key] == 1].to_dict(orient='record')
        cur_grid_type: GridTypeDetail = GridTypeDetailDomainSchema().load(cur, many=True)[0]
        cur_detail_df: DataFrame = DataFrame()
        # 如果当天数据的收盘价大于等于监控数据的卖出触发价，当价格处于网格边界时，需要判断等于的状态
        if today_daily_data.f_close >= cur_grid_type.trigger_sell_price:
            cur_detail_df: DataFrame = detail_df[
                (detail_df[GridTypeDetail.trigger_purchase_price.key] <= today_daily_data.f_close) &
                (detail_df[GridTypeDetail.trigger_sell_price.key] > today_daily_data.f_close)]
        # 如果当天数据的收盘价小于等于监控数据的买入触发价，当价格处于网格边界时，需要判断等于的状态
        elif today_daily_data.f_close <= cur_grid_type.trigger_purchase_price:
            cur_detail_df: DataFrame = detail_df[
                (detail_df[GridTypeDetail.trigger_purchase_price.key] < today_daily_data.f_close) &
                (detail_df[GridTypeDetail.trigger_sell_price.key] >= today_daily_data.f_close)]
        # 如果存在数据，判断该数据档位与当前监控档位是否相同
        if len(cur_detail_df) > 0 and cur_detail_df.iloc[0][GridTypeDetail.gear.key] != cur_grid_type.gear:
            return [cur_grid_type.id, cur_detail_df.iloc[0][GridTypeDetail.id.key]]
        # 如果存在数据，且该与当前档位相同，不需要更改档位
        elif len(cur_detail_df) > 0 and cur_detail_df.iloc[0][GridTypeDetail.gear.key] == cur_grid_type.gear:
            return []
        # 如果数据不存在，且收盘价比最小网格的买入价要高，说明当前的价格在网格范围之内，但不在网格监控范围内，不需要更改档位数据
        elif len(cur_detail_df) == 0 and \
                today_daily_data.f_close > detail_df.iloc[-1][GridTypeDetail.trigger_purchase_price.key]:
            return []
        # 如果不存在数据，说明可能当前的价格已经在网格之外了
        # 判断当前监控档位是否为最小档位，如果不是，修改监控档位
        loc_index = 0 if today_daily_data.f_close >= cur_grid_type.trigger_purchase_price else -1
        if cur_grid_type.gear != detail_df.iloc[loc_index][GridTypeDetail.gear.key]:
            return [cur_grid_type.id, detail_df.iloc[loc_index][GridTypeDetail.id.key]]


grid_service = GridService()
