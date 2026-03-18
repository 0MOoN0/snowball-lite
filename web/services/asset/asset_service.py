import numbers
import random
import time
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
from pandas import DataFrame
from sqlalchemy import or_

from web.common.cons import webcons
from web.common.enum.asset_enum import AssetTypeEnum
from web.databox import databox
from web.decorator import singleton
from web.models import db
from web.models.asset.asset import Asset, AssetCurrentDTO
from web.models.asset.asset_code import AssetCode
from web.models.asset.AssetFundDailyData import AssetFundDailyData, AssetFundDailyDataSchema
from web.models.asset.AssetFundFeeRule import AssetFundFeeRule
from web.models.asset.AssetHoldingData import AssetHoldingData
from web.models.grid.GridType import GridType
from web.web_exception import WebBaseException
from web.weblogger import logger


@singleton
class AssetService:
    def init_fund_asset_data(self, asset_code: AssetCode):
        """
        根据给定参数获取资产数据并存入数据库，如果天天基金代码不存在，则无法获取持仓数据和净值数据
        Args:
            asset_code(AssetCode): 资产代码对象

        Returns:

        """
        asset_id = asset_code.asset_id
        code_ttjj = asset_code.code_ttjj
        code_xq = asset_code.code_xq
        if asset_id is None:
            raise WebBaseException(msg="缺少参数：asset_id is required")
        count = AssetFundDailyData.query.filter(AssetFundDailyData.asset_id == asset_id).count()
        if count > 0:
            logger.info("资产ID为：{} 的数据已经存在，请调用同步数据的方法对数据进行同步".format(asset_id))
            # 调用同步数据的方法进行同步
            return
        daily_data_df = pd.DataFrame()
        ttjj_data_df = pd.DataFrame()
        xq_data_df = pd.DataFrame()
        # 获取净值数据
        if code_ttjj is not None:
            # 记录基金信息，托管费目前可能没办法获取
            fund_info = databox.fund_info(code_ttjj)
            if fund_info is not None:
                # 基金日常数据
                ttjj_data_df = fund_info.price
                ttjj_data_df.sort_values('date', inplace=True)
                rules = self._get_fee_rules(fund_info.rate, fund_info.feeinfo, asset_id)
                # 保存基金费用规则信息
                db.session.add_all(rules)
                db.session.flush()
        # 获取日线数据
        if code_xq is not None:
            xq_data_df = databox.fetch_online_daily_data(code_xq)
            if xq_data_df and ttjj_data_df:
                # 合并数据，显示两边的数据，key为date，并根据date排序
                daily_data_df = pd.merge(ttjj_data_df, xq_data_df, how='outer', on=['date'], sort='date')
        # 当天天基金数据或雪球数据不存在时，需要将天天基金或雪球数据中的一个作为日线数据
        if len(daily_data_df) == 0:
            daily_data_df = ttjj_data_df if len(ttjj_data_df) > 0 else xq_data_df
        daily_data_objects = self.convert_df_to_daily_data(daily_data_df, asset_id)
        # 批量插入
        AssetFundDailyData.query.filter(AssetFundDailyData.asset_id == asset_id).delete()
        db.session.bulk_save_objects(daily_data_objects, return_defaults=True, update_changed_only=False)
        db.session.flush()
        # 分时信息（待定）
        # 获取持仓数据
        if code_ttjj is None:
            logger.info(
                'asset_id: {asset_id} 资产数据添加成功，由于基金代码数据不足，因此无法获取持仓信息'.format(asset_id))
            return
        # 获取最近一次的持仓信息，如果不满第一季度的日期，就改为获取上一年最后一个季度的数据，季度从1开始
        today = datetime.today()
        quarter = int(today.month / 3) - 1
        year = today.year - 1 if quarter <= 0 else today.year
        quarter = 4 if quarter <= 0 else quarter
        position_df = fund_info.get_stock_holdings(year, season=quarter)
        if position_df is None or len(position_df) == 0:
            year, quarter = self._get_previous_quarter(year, quarter)
            # 获取再上一个季度的持仓信息，如果持仓信息仍不存在，结束方法
            position_df = fund_info.get_stock_holdings(year, season=quarter)
            if position_df is None or len(position_df) == 0:
                logger.info('asset_id: {asset_id} 股票持仓信息为空'.format(asset_id))
                db.session.commit()
                return
        positions = []
        for index, position in position_df.iterrows():
            code = position['code'].split('.')[0]
            # 根据代码形式构造查询条件
            query_condition = []
            # 如果是五位数字，使用等值查询，否则使用模糊查询
            if code.isdigit() and len(code) == 5:
                query_condition.append(AssetCode.code_xq == code)
            else:
                query_condition.append(AssetCode.code_xq.like(f'%{code}'))
            # 判断持仓信息是否已经存在
            asset_count = db.session.query(Asset).join(AssetCode, Asset.id == AssetCode.asset_id) \
                .filter(*query_condition, Asset.asset_type == Asset.get_asset_type_enum().STOCK.value) \
                .count()
            # 判断assets长度是否大于1，如果大于1，表示无法处理，打印日志并跳过
            if asset_count > 1:
                # 抛出数据错误异常
                raise ValueError('获取 %s 股票数据错误，获取的数据大于1条，无法处理该数据' % code)
            asset = db.session.query(Asset).join(AssetCode, Asset.id == AssetCode.asset_id) \
                .filter(*query_condition, Asset.asset_type == Asset.get_asset_type_enum().STOCK.value) \
                .first()
            # 如果数据库不存在该数据，就创建一个
            if asset is None:
                asset: Asset = Asset()
                asset.asset_type = AssetTypeEnum.STOCK.value
                # 获取资产货币类型
                # 获取资产当前信息
                current_data: AssetCurrentDTO = databox.get_rt(code=code)
                if current_data is None:
                    logger.exception('获取 %s 股票数据错误，获取的数据为空' % code)
                    continue
                asset.asset_name = current_data.name
                asset.market = current_data.market
                db.session.add(asset)
                db.session.flush()
                asset_code = AssetCode()
                asset_code.code_xq = current_data.code
                asset_code.asset_id = asset.id
                db.session.add(asset_code)
                db.session.flush()
            # 创建asset_holding_data对象
            asset_holding_data = AssetHoldingData()
            asset_holding_data.ah_date = datetime.now()
            asset_holding_data.ah_asset_name = asset.asset_name
            # 当前数据的asset_id
            asset_holding_data.asset_id = asset.id
            # 持有者的asset_id
            asset_holding_data.ah_holding_asset_id = asset_id
            asset_holding_data.ah_holding_percent = int(position['ratio'] * 100)
            asset_holding_data.ah_quarter = quarter
            asset_holding_data.ah_year = year
            positions.append(asset_holding_data)
            time.sleep(3 + random.randint(0, 2))
        db.session.add_all(positions)
        # 提交事务，报错信息
        db.session.commit()

    def init_index_asset_data(self, asset_code: AssetCode):
        """
        根据资产ID和指数代码初始化指数数据，代码会从雪球中获取数据，并存储到数据库中，此数据是指数数据，没有净值等内容
        Args:
            asset_code: 资产代码对象
        Returns:

        """
        code_index = asset_code.code_index
        asset_id = asset_code.asset_id
        # 判断code_index和asset_id是否为空
        if code_index is None or asset_id is None:
            # 抛出AttributeError异常
            raise AttributeError('asset_code的code_index和asset_id不能为空')
        count = AssetFundDailyData.query.filter(AssetFundDailyData.asset_id == asset_id).count()
        if count > 0:
            logger.info("资产ID为：{} 的数据已经存在，请调用同步数据的方法对数据进行同步".format(asset_id))
            # 调用同步数据的方法进行同步
            return
        daily_data_df = databox.fetch_online_daily_data(asset_code.code_index)
        daily_data_list = self.convert_df_to_daily_data(daily_data_df, asset_id)
        db.session.bulk_save_objects(daily_data_list, return_defaults=False, update_changed_only=False)
        db.session.commit()

    def _get_fee_rules(self, purchase_rate: float, feeinfo: list, asset_id: numbers):
        """
        解析给定数据，获取费用规则（暂不解析赎回费用规则）
        Args:
            purchase_rate (float): 申购费，一般为百分比
            feeinfo (list): string数组，赎回费用的描述
            asset_id (number): 资产ID

        Returns:
            返回一个数组，内容为封装好的费用规则对象
        """
        rules = []
        purchase_rule = AssetFundFeeRule.get_purchase_rule(rate=purchase_rate, asset_id=asset_id)
        rules.append(purchase_rule)
        # 不解析赎回费用规则
        # rules.extend(AssetFundFeeRule.get_redemption_rule(feeinfo=feeinfo, asset_id=asset_id))
        return rules

    def _get_previous_quarter(self, year: numbers, quarter: numbers):
        if quarter - 1 > 0:
            return year, quarter - 1
        return year - 1, 4

    def get_asset_by_code(self, code: str) -> Asset:
        """
        根据代码获取相关证券信息
        Args:
            code: str, not None，代码，天天基金代码或者雪球代码

        Returns: Asset类型

        """
        return db.session.query(Asset).join(AssetCode, AssetCode.asset_id == Asset.id, isouter=True) \
            .filter(or_(AssetCode.code_xq == code, AssetCode.code_ttjj == code)).first()

    def get_asset_by_grid_id(self, grid_type_id: int) -> Asset:
        return db.session.query(Asset).join(GridType, GridType.asset_id == Asset.id, isouter=True) \
            .filter(GridType.id == grid_type_id).first()

    def convert_df_to_daily_data(self, daily_data_df: DataFrame, asset_id: int) -> List[AssetFundDailyData]:
        """
        将DataFrame格式的日线数据转换为AssetFundDailyData对象列表。

        Args:
            daily_data_df (DataFrame): 包含日线数据的DataFrame，其中必须包含'date', 'netvalue', 'comment',
                'totvalue', 'open', 'close', 'high', 'low', 'volume', 'percent'等列。
            asset_id (int): 资产的唯一标识符。

        Returns:
            List[AssetFundDailyData]: 包含转换后的AssetFundDailyData对象的列表。

        Raises:
            无特定异常，但可能在数据处理过程中抛出异常（如数据类型转换错误）。

        """
        if len(daily_data_df) == 0:
            return []
        columns = {
            'date': 'f_date',
            'netvalue': 'f_netvalue',
            'comment': 'f_comment',
            'totvalue': 'f_totvalue',
            'open': 'f_open',
            'close': 'f_close',
            'high': 'f_high',
            'low': 'f_low',
            'volume': 'f_volume',
            'percent': 'f_close_percent'
        }
        # 删除所有date列所在行是None的数据
        daily_data_df.dropna(axis=0, how='any', inplace=True, subset=["date"])
        daily_data_df['asset_id'] = asset_id
        daily_data_df.rename(columns=columns, inplace=True)
        # 不需要修改的类型的列
        columns_to_keep = ['f_date', 'asset_id', 'f_volume']
        # 选出需要转换数据类型的列，并进行转换
        columns_to_convert = daily_data_df.columns.difference(columns_to_keep)
        # 类型转换，将float64转为Int64
        daily_data_df[columns_to_convert] = np.floor(daily_data_df[columns_to_convert] * 10000).astype('Int64')
        # 去除NA数据，将NA数据转换为None
        daily_data_df.replace({np.nan: None}, inplace=True)
        # 处理时间数据，将数据转换成字符串，以便Schema转换
        daily_data_df['f_date'] = daily_data_df['f_date'].apply(lambda x: x.strftime(webcons.DataFormatStr.Y_m_d_H_M_S))
        # 转换为字典列表，再通过Schema转换为对象列表
        daily_datas = daily_data_df.to_dict(orient='records')
        daily_data_objects = AssetFundDailyDataSchema().load(daily_datas, many=True)

        return daily_data_objects


asset_service: AssetService = AssetService()
