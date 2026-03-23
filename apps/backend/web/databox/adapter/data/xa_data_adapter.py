import uuid
from contextlib import nullcontext
from datetime import datetime, timedelta
from typing import List, Tuple, Dict

import numpy as np
import pandas as pd
from flask import has_app_context
from marshmallow import EXCLUDE
from pandas import DataFrame

from web import models
from web.common.cons import webcons
from web.common.enum.common_enum import CurrencyEnum
from web.common.utils.WebUtils import webutils
from web.databox.adapter.data.DataBoxDataAdapter import DataBoxDataAdapter
from web.databox.adapter.data.xa_service import XaService
from web.databox.adapter.record.RecordAdapter import XaRecordAdapter, RecordAdapter
from web.web_exception.WebException import WebAnalyzerException
from web.models import db
from web.models.asset.asset import AssetCurrentDTO, Asset
from web.models.asset.asset_code import AssetCode
from web.models.asset.AssetFundDailyData import AssetFundDailyData, AssetFundDailyDataSchema
from web.models.asset.AssetHoldingData import AssetHoldingDataDTO, AssetHoldingDataDTOSchema
from web.models.record.record import Record
from web.weblogger import error, info, warning
from xalpha import mul, fundinfo
from xalpha.cons import yesterdayobj
import xalpha as xa


class XaDataAdapter(DataBoxDataAdapter, XaService):
    def fundinfo(self, code: str, **kwargs):
        fund_info_kwargs = self._get_fund_info_db_setting()
        fund_info_kwargs.update(kwargs)
        return self.xa.fundinfo(code=code, **fund_info_kwargs)

    def __init__(self, code_ttjj: str = None, code_xq: str = None, asset_code: AssetCode = None):
        # 代码相关信息
        self.fund_info_db_setting = {}
        self.xa = xa
        self.code_ttjj = code_ttjj
        self.code_xq = code_xq
        self.asset_code = asset_code
        self.record_adapter: RecordAdapter = XaRecordAdapter()
        # 交易数据缓存，key为交易方法返回的ID，value为trade对象
        self.trade_cache = dict()
        # 基金数据缓存，key为基金代码code_ttjj，value为fundinfo对象
        self.fund_info_cache = dict()

    def init_adapter(self, xq_token: Dict):
        info("开始初始化XaDataAdapter")
        self.xa.universal.set_token(xq_token)
        cache_settings = webcons.apply_xalpha_cache_settings(
            self.xa,
            default_engine=models.db.engine,
        )
        self.fund_info_db_setting = dict(cache_settings["fundinfo"])
        info("XaDataAdapter初始化完成")

    def _get_fund_info_db_setting(self) -> Dict:
        if has_app_context():
            if webcons.XaFundInfoSetting.DB_SETTING:
                self.fund_info_db_setting = dict(webcons.XaFundInfoSetting.DB_SETTING)
                return dict(self.fund_info_db_setting)

            cache_settings = webcons.resolve_xalpha_cache_settings(
                default_engine=models.db.engine,
            )
            self.fund_info_db_setting = dict(cache_settings["fundinfo"])
            return dict(self.fund_info_db_setting)

        if self.fund_info_db_setting:
            return dict(self.fund_info_db_setting)

        return dict(self.fund_info_db_setting)

    def _daily_backend_scope(self):
        if not has_app_context():
            return None

        return webcons.xalpha_daily_backend_scope(
            self.xa,
            default_engine=models.db.engine,
        )

    def get_stock_holdings(self, code: str, year: int, quarter: int) -> List[AssetHoldingDataDTO]:
        """
        获取证券的股票持仓数据，因为数据接口能力限制，暂时无法获取FOF基金的持仓数据
        从stock_info中获取的股票持仓数据fund_holding，类型为DataFrame，需要转换JSON，再通过AssetHoldingDataDTOSchema转换为为AssetHoldingDataDTO
        stock_holding包含code, name, ratio, share, value列，分别对应代码，名称，占持仓比例，持股数量(万股)，持股市值（万元人民币）
        Args:
            code (str): 基金代码
            year (int): 年份
            quarter (int):  季度

        Returns:
            List[AssetHoldingDataDTO]: 股票持仓数据，如果没有持仓数据，返回空列表
        """
        info(f"开始获取基金 {code} 在 {year}年第{quarter}季度的持仓数据")
        fund_info: fundinfo = self.fund_info_cache.get(code)
        if fund_info is None:
            info(f"基金 {code} 的信息不在缓存中，从网络获取")
            fund_info = self.fundinfo(code=code)
            self.fund_info_cache.update({code: fund_info})
        stock_holding: DataFrame = fund_info.get_stock_holdings(year=year, season=quarter)
        # stock_holding可能为空或空列表，如果为空，返回空列表
        if stock_holding is None or stock_holding.empty:
            info(f"基金 {code} 在 {year}年第{quarter}季度没有持仓数据")
            return []
        # 处理ratio,share,value，乘以100并转换为int类型
        stock_holding['ratio'] = (stock_holding['ratio'] * 100).astype(int)
        # 根据code作为天天基金代码，获取资产数据
        currency = db.session.query(Asset.currency).join(AssetCode, AssetCode.asset_id == Asset.id).filter(
            AssetCode.code_ttjj == code).first().currency
        # 判断是否为美元
        if Asset.get_currency_enum().USD == CurrencyEnum(currency):
            info(f"基金 {code} 的货币为美元，调整持仓股票代码格式")
            # 分割持仓的code的字段，获取第一个.符号的前面字符作为code
            stock_holding['code'] = stock_holding['code'].str.split('.').str[0]
        asset_holding_data_dto_schema = AssetHoldingDataDTOSchema()
        result = asset_holding_data_dto_schema.loads(stock_holding.to_json(orient='records'), many=True)
        info(f"成功获取基金 {code} 在 {year}年第{quarter}季度的持仓数据，共 {len(result)} 条")
        return result

    def get_rt(self, code: str = None) -> AssetCurrentDTO:
        """
        方法内容：根据代码获取资产实时信息，返回一个AssetCurrentDTO对象，数据来源是雪球
            get_rt方法获取港股数据的可以使用HK前缀，也可以不使用HK前缀
        注意：
        方法实现：调用xa的get_rt方法，得到一个字典对象，其中name为资产名称，current为资产价格，单位元，需要转换为厘并用整数存储，
            然后转换为AssetCurrentDTO返回
        Args:
            code (str): 资产代码，在系统中对应的是雪球代码

        Returns:
            AssetCurrentDTO: 资产实时信息
        """
        # 判断code是否为空
        if self.code_xq is None and code is None:
            error("获取实时数据时代码为空")
            raise RuntimeError('代码不能为空，请在使用前设置代码或者传入代码')
        code = code if code is not None else self.code_xq
        info(f"开始获取代码 {code} 的实时数据")
        rt = self.xa.get_rt(code=code)
        if rt is None:
            # 记录数据不存在的error日志
            info('数据不存在，请检查代码:  %s ' % code)
            return None
        market = Asset.get_market_enum()[rt.get('market')].value if rt.get('market') is not None else None
        currency = Asset.get_currency_enum()[rt.get('currency')].value if rt.get('currency') is not None else None
        asset_current_dto = AssetCurrentDTO(name=rt['name'], code=code, price=int(rt['current'] * 1000),
                                            market=market, currency=currency)
        info(f"成功获取代码 {code} 的实时数据，资产名称: {rt['name']}, 当前价格: {rt['current']}")
        return asset_current_dto

    def get_core(self):
        return self.xa

    def trade(self, records: List[Record]):
        """
        方法内容：交易分析方法，交易数据存储在trade_cache中，key为交易方法返回的ID，value为trade对象，场内交易使用的是雪球的接口，场外交易使用的是天天基金的接口
        Args:
            records ():

        Returns:

        """
        record_df = self.record_adapter.convert_record(records)
        raw_asset_ids = [int(asset_id) for asset_id in pd.unique(record_df["asset_id"].dropna())]
        # 获取基金代码
        asset_codes: List[AssetCode] = AssetCode.query.filter(
            AssetCode.asset_id.in_(raw_asset_ids)
        ).all()
        # 高效地将asset_id映射为code_xq
        asset_code_map = {
            asset_code.asset_id: asset_code.code_xq
            for asset_code in asset_codes if asset_code.code_xq
        }
        missing_asset_ids = [
            asset_id for asset_id in raw_asset_ids if asset_id not in asset_code_map
        ]
        if missing_asset_ids:
            raise WebAnalyzerException(
                msg=f"asset_id {missing_asset_ids} 对应的雪球代码不存在"
            )
        record_df['asset_id'] = record_df['asset_id'].map(asset_code_map)
        record_df.rename(columns={'asset_id': 'code'}, inplace=True)
        trade_result = self.xa.mul(istatus=record_df)
        # 生成uuid的无符号整数形式
        cache_id: int = uuid.uuid4().int
        self.trade_cache.update({cache_id: trade_result})
        # 获取交易数据
        return cache_id

    def summary(self, trade_id: int, date=None) -> DataFrame:
        """
        获取交易总览。

        Args:
            trade_id (int): 交易数据缓存ID。
            date (str, optional): 交易总览日期，默认为None，即查询当天的交易总览。可以是一个日期格式的字符串。

        Returns:
            DataFrame: 交易总览数据，包含多列，其中一列为总计数据，其他列为交易基金对应的总览数据。
                包含字段：["基金名称","基金代码","当日净值","单位成本","持有份额","基金现值","基金总申购",
                "历史最大占用","基金持有成本","基金分红与赎回","换手率","基金收益总额","投资收益率","内部收益率"]

        Raises:
            WebAnalyzerException: 如果交易记录不存在或交易日期不在交易范围内，将抛出此异常。

        """
        trade_result: mul = self.trade_cache.get(trade_id)
        if trade_result is None:
            error('summary 交易记录不存在， trade_id : %d ' % trade_id)
            raise WebAnalyzerException(msg='交易记录不存在')
        if date is None:
            date = yesterdayobj()
        else:
            date = webutils.convert_date(date)
        if date < trade_result.totcftable.iloc[0].date:
            error(f'summary 日期不在交易范围内，trade_id: {trade_id}, date: {date}')
            raise WebAnalyzerException(msg='summary 交易日期不在交易范围内')
        summary = trade_result.combsummary(date=date)
        summary['内部收益率'] = np.nan
        summary['年化收益率'] = np.nan
        for fund_trade in trade_result.fundtradeobj:
            # irr的计算使用了optimize.newton对初始化值很敏感，因此开始时的偏差可能会很大，因此只从第一次交易的开始后10天才开始计算irr
            fund_irr_start_date = fund_trade.cftable.iloc[0].date + timedelta(days=webcons.XAIRRDelayDate.DELAY_DATE)
            if fund_irr_start_date < date:
                # 捕获异常
                try:
                    fund_irr = fund_trade.xirrrate(date=date)
                    summary.loc[summary['基金名称'] == fund_trade.name, '内部收益率'] = fund_irr
                except Exception as e:
                    error(f'基金： {fund_trade.name} - 日期： {date} 内部收益率计算失败，错误信息：{e}', exc_info=True)
            
            # 计算年化收益率
            try:
                fund_start_date = fund_trade.cftable.iloc[0].date
                holding_days = (date - fund_start_date).days
                if holding_days > 0:
                    investment_return = summary.loc[summary['基金名称'] == fund_trade.name, '投资收益率'].values[0]
                    cagr = ((1 + (investment_return / 100)) ** (365 / holding_days)) - 1
                    summary.loc[summary['基金名称'] == fund_trade.name, '年化收益率'] = cagr
            except Exception as e:
                error(f'基金： {fund_trade.name} - 日期： {date} 年化收益率计算失败，错误信息：{e}', exc_info=True)

        summary_irr_start_date = trade_result.totcftable.iloc[0].date + timedelta(
            days=webcons.XAIRRDelayDate.DELAY_DATE)
        if summary_irr_start_date < date:
            # 捕获异常
            try:
                summary.loc[summary['基金名称'] == '总计', '内部收益率'] = trade_result.xirrrate(date=date)
            except Exception as e:
                error(f'总计数据日期：{date} 内部收益率计算失败，错误信息：{e}', exc_info=True)
        
        # 计算总计年化收益率
        try:
            total_start_date = trade_result.totcftable.iloc[0].date
            total_holding_days = (date - total_start_date).days
            if total_holding_days > 0:
                total_investment_return = summary.loc[summary['基金名称'] == '总计', '投资收益率'].values[0]
                total_cagr = ((1 + (total_investment_return / 100)) ** (365 / total_holding_days)) - 1
                summary.loc[summary['基金名称'] == '总计', '年化收益率'] = total_cagr
        except Exception as e:
            error(f'总计数据日期：{date} 年化收益率计算失败，错误信息：{e}', exc_info=True)
            
        return summary

    def get_trade_fund_name(self, trade_id: int) -> tuple:
        """
            根据交易ID从缓存中获取交易数据的基金名称，以元组的形式返回
        抛出异常：当trade_id对应的交易缓存数据不存在时，将抛出交易分析异常：WebAnalyzerException
        Args:
            trade_id: 交易缓存ID
        Returns:
            基金名称数据元组，如：('华宝油气LOF')
        """
        trade_result: mul = self.trade_cache.get(trade_id)
        if trade_result is None:
            error('get_trade_fund 交易记录不存在， trade_id : %d ' % trade_id)
            raise WebAnalyzerException(msg='交易记录不存在')
        return tuple(fund.name for fund in trade_result.fundtradeobj)

    def get_daily(self, start_date: datetime, end_date: datetime, asset_code: AssetCode = None) -> List[
        AssetFundDailyData]:
        """
        方法内容：获取资产指定日期范围的日线数据，返回一个AssetFundDailyData对象，如果asset_code里面的code_ttjj数据不存在，则无法获取相关净值
        设计目的：用于从外部获取资产的日线数据，数据来源是天天基金网和雪球网
        方法实现：缓存中是否有fund_info数据，如果有则先校验日期数据是否符合，如果不符合，则重新获取并更新缓存
                调用xa的get_daily方法，获取资产的日线数据
                最后组装并返回AssetFundDailyData对象
        Args:
            asset_code (AssetCode): 资产代码，会用到code_xq和code_ttjj
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期

        Returns:
            AssetFundDailyData: 资产日线数据
        """
        backend_scope = self._daily_backend_scope() or nullcontext()
        with backend_scope as cache_settings:
            if cache_settings is not None:
                self.fund_info_db_setting = dict(cache_settings["fundinfo"])

            info(f"开始获取日线数据，start_date: {start_date}, end_date: {end_date}")
            ttjj_df: DataFrame = None
            xq_df: DataFrame = None
            start_date, end_date, code_ttjj, code_xq, asset_code = self._format_get_daily_input(start_date, end_date,
                                                                                                asset_code)
            info(f"格式化后的参数: start_date={start_date}, end_date={end_date}, code_ttjj={code_ttjj}, code_xq={code_xq}")
            if code_ttjj:
                info(f"开始获取代码 {code_ttjj} 的天天基金日线数据")
                # 获取天天基金代码，如果传入的天天基金代码为空，则使用缓存中的天天基金代码
                fund_info = self.fund_info_cache.get(code_ttjj)
                price: DataFrame = None
                ttjj_price = None
                if fund_info is not None:
                    price = fund_info.price.copy(deep=True)
                    ttjj_price = price.loc[
                        (price.date >= start_date) & (price.date <= end_date)
                    ].copy()
                # 判断日期是否存在
                if fund_info is None or ttjj_price.empty:
                    info(f"基金 {code_ttjj} 的缓存中无指定日期范围数据，从网络获取")
                    fund = self.fundinfo(code=code_ttjj)
                    price = fund.price.copy(deep=True)
                    self.fund_info_cache.update({code_ttjj: fund})
                    # 再次检查
                    ttjj_price = price.loc[(price.date >= start_date) & (price.date <= end_date)].copy()
                    if not ttjj_price.empty:
                        info(f"成功获取基金 {code_ttjj} 的日线数据，记录数: {len(ttjj_price)}")
                    else:
                        info(f"基金 {code_ttjj} 在指定日期范围内无日线数据")
                if ttjj_price is not None and not ttjj_price.empty:
                    ttjj_df = ttjj_price
                    # 修改字段
                    ttjj_df.rename(columns={'date': 'f_date', 'netvalue': 'f_netvalue', 'totvalue': 'f_totvalue',
                                            'comment': 'f_comment'},
                                   inplace=True)
            # 获取雪球日线数据
            if code_xq:
                info(f"开始获取代码 {code_xq} 的雪球日线数据")
                # 获取雪球代码，如果传入的雪球代码为空，则使用缓存中的雪球代码
                xq_df = self.xa.get_daily(code=code_xq, start=start_date, end=end_date)
                # 判断数据是否存在
                if not xq_df.empty:
                    info(f"成功获取代码 {code_xq} 的雪球日线数据，记录数: {len(xq_df)}")
                    xq_df.rename(columns={'date': 'f_date', 'open': 'f_open', 'close': 'f_close', 'high': 'f_high',
                                          'low': 'f_low', 'volume': 'f_volume', 'percent': 'f_close_percent'},
                                 inplace=True)
                else:
                    info(f"代码 {code_xq} 在指定日期范围内无雪球日线数据")
            # 如果有数据则转换为AssetFundDailyData对象列表
            if ttjj_df is not None or xq_df is not None:
                info("开始合并日线数据")
                # 合并数据
                if ttjj_df is not None and xq_df is not None:
                    df = pd.merge(ttjj_df, xq_df, on='f_date', how='outer')
                    info(f"合并天天基金和雪球数据，合并后记录数: {len(df)}")
                elif ttjj_df is not None:
                    df = ttjj_df
                    info("只使用天天基金数据")
                else:
                    df = xq_df
                    info("只使用雪球数据")
                # 如果asset_code不为空，则添加asset_id列
                if asset_code is not None:
                    df['asset_id'] = asset_code.asset_id
                    info(f"为日线数据添加资产ID: {asset_code.asset_id}")
                # 使用AssetFundDailyDataSchema转换为对象
                result = self._convert_daily_data(df)
                info(f"日线数据转换完成，返回记录数: {len(result)}")
                return result
            info("无法获取日线数据，返回空列表")
            return []

    @staticmethod
    def _convert_daily_data(daily_data: DataFrame) -> List[AssetFundDailyData]:
        """
        转换日线数据，将DataFrame数字转换成整数后，再转换为AssetFundDailyData对象列表
        Args:
            daily_data (DataFrame): 日线数据

        Returns:

        """
        # 判断长度是否大于0
        if len(daily_data) == 0:
            info("日线数据为空，返回空列表")
            return []
        info(f"开始转换日线数据，记录数: {len(daily_data)}")
        daily_data['f_date'] = daily_data['f_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        # 不需要修改的类型的列
        except_columns = ['f_date', 'asset_id', 'f_volume']
        # 需要修改的类型的列
        need_columns = [column for column in daily_data.columns if column not in except_columns]
        # 类型转换，将float64乘以10000并转为Int64
        daily_data[need_columns] = np.floor(daily_data[need_columns] * 10000).astype('Int64')
        # 去除NA数据，将NA数据转换为None
        daily_data.replace({np.nan: None}, inplace=True)
        result = AssetFundDailyDataSchema().loads(daily_data.to_json(orient='records'), many=True, unknown=EXCLUDE)
        info(f"日线数据转换完成，转换后记录数: {len(result)}")
        return result

    def _format_get_daily_input(self, start_date: datetime, end_date: datetime, asset_code: AssetCode = None) -> Tuple[
        str, str, str, str, AssetCode]:
        """
        方法内容：处理获取日线数据的输入参数，如果部分参数为空，则尝试使用对象变量中的数据，日期格式化处理，将日期格式化为yyyy-mm-dd，
                返回内容顺序为start_date, end_date, code_ttjj, code_xq, asset_code
        Args:
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期
            asset_code (AssetCode): 资产代码

        Returns:

        """
        info("开始格式化日线数据输入参数")
        if asset_code is not None:
            code_ttjj = asset_code.code_ttjj
            code_xq = asset_code.code_xq
            asset_code = asset_code
        else:
            code_ttjj = self.code_ttjj
            code_xq = self.code_xq
            asset_code = self.asset_code
        # 如果日期格式不为空，转换日期格式为：yyyy-mm-dd
        if start_date is not None:
            start_date = start_date.strftime('%Y-%m-%d')
        if end_date is not None:
            end_date = end_date.strftime('%Y-%m-%d')
        info(f"格式化后的参数: start_date={start_date}, end_date={end_date}, code_ttjj={code_ttjj}, code_xq={code_xq}")
        return start_date, end_date, code_ttjj, code_xq, asset_code

    def fetch_daily_data(self, asset_code: AssetCode = None, asset_id: int = None, start_date: datetime = None,
                           end_date: datetime = None) -> List[AssetFundDailyData]:
        """
        获取日线数据的方法，用于直接获取日线数据，参数更加灵活，支持传入asset_code或asset_id，以及开始日期和结束日期
        Args:
            asset_code: 资产代码对象
            asset_id: 资产ID
            start_date: 开始日期，如果为None，则使用7天前的日期
            end_date: 结束日期，如果为None，则使用当前日期

        Returns:
            日线数据列表
        """
        info(f"开始获取日线数据，asset_id={asset_id}, start_date={start_date}, end_date={end_date}")
        # 如果asset_code和asset_id都为空，则使用self.asset_code
        if asset_code is None and asset_id is None:
            asset_code = self.asset_code
            info(f"使用默认asset_code: {asset_code}")
        # 如果asset_code为空，并且asset_id不为空，则根据asset_id获取asset_code
        if asset_code is None and asset_id is not None:
            info(f"根据asset_id={asset_id}查询asset_code")
            asset_code = db.session.query(AssetCode).filter(AssetCode.asset_id == asset_id).first()
        # 如果开始日期为空，则使用7天前的日期
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
            info(f"未指定start_date，使用7天前: {start_date}")
        # 如果结束日期为空，则使用当前日期
        if end_date is None:
            end_date = datetime.now()
            info(f"未指定end_date，使用当前日期: {end_date}")
            
        # 获取日线数据
        try:
            info(f"调用get_daily获取日线数据，start_date={start_date}, end_date={end_date}, asset_code={asset_code}")
            daily_data = self.get_daily(start_date=start_date, end_date=end_date, asset_code=asset_code)
            
            if daily_data and asset_code and asset_code.asset_id:
                # 获取已经存在的日期记录
                info(f"检查是否存在重复数据，asset_id={asset_code.asset_id}")
                existing_dates = set()
                try:
                    # 查询日期范围内该资产已存在的日线数据记录
                    formatted_start = start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime) else start_date
                    formatted_end = end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else end_date
                    
                    existing_records = db.session.query(AssetFundDailyData.f_date)\
                        .filter(AssetFundDailyData.asset_id == asset_code.asset_id)\
                        .filter(AssetFundDailyData.f_date >= formatted_start)\
                        .filter(AssetFundDailyData.f_date <= formatted_end)\
                        .all()
                    
                    for record in existing_records:
                        if hasattr(record, 'f_date'):
                            # 如果f_date是datetime对象，转为字符串
                            date_str = record.f_date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(record.f_date, datetime) else str(record.f_date)
                            existing_dates.add(date_str)
                    
                    info(f"找到 {len(existing_dates)} 条已存在的日线数据记录")
                    
                    # 过滤掉已存在的日期记录
                    filtered_daily_data = []
                    for data in daily_data:
                        date_str = data.f_date if isinstance(data.f_date, str) else data.f_date.strftime('%Y-%m-%d %H:%M:%S')
                        if date_str not in existing_dates:
                            filtered_daily_data.append(data)
                        else:
                            info(f"过滤掉重复的日线数据，日期: {date_str}")
                    
                    removed_count = len(daily_data) - len(filtered_daily_data)
                    if removed_count > 0:
                        info(f"过滤掉 {removed_count} 条重复数据")
                    
                    daily_data = filtered_daily_data
                except Exception as e:
                    error(f"检查重复数据异常: {str(e)}", exc_info=True)
                    # 记录异常但继续执行，避免因为去重功能影响主流程
            
            info(f"成功获取日线数据，返回记录数: {len(daily_data)}")
            return daily_data
        except Exception as e:
            error(f"获取日线数据异常: {str(e)}", exc_info=True)
            # 打印异常日志
            error(f"asset_code: {asset_code}, start_date: {start_date}, end_date: {end_date}")
            # 抛出异常
            raise e
