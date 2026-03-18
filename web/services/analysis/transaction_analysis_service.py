from _decimal import Decimal
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Union, Tuple, Optional, Dict

import pandas
import pandas as pd
from pandas import DataFrame

from web.common.cons import webcons
from web.common.enum.AnalysisEnum import TransactionAnalysisTypeEnum
from web.common.utils.WebUtils import webutils
from web.databox import databox
from web.models import db
from web.models.analysis.amount_trade_analysis_data import AmountTradeAnalysisData
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.asset.asset_code import AssetCode
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail, GridTypeDetailDomainSchema
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.record.record import Record


class TradeAnalysisService(ABC):

    def __init__(self):
        """
        初始化方法。

        Args:
            无

        Returns:
            无

        """
        self.records: List[Record] = []

    def trade_analysis(
        self, start: Union[datetime, str] = None, end: Union[datetime, str] = None
    ):
        """
        进行交易分析。

        Args:
            start (Union[datetime, str], optional): 分析的起始时间，默认为None，表示使用当天日期。
                如果为datetime对象，则直接使用该日期；如果为字符串，则尝试转换为datetime对象。
                Defaults to None.
            end (Union[datetime, str], optional): 分析的结束时间，默认为None，表示使用当天日期。
                如果为datetime对象，则直接使用该日期；如果为字符串，则尝试转换为datetime对象。
                Defaults to None.

        Returns:
            None

        """
        records: List[Record] = self.get_trade_analysis_record()
        self.records = records
        if not records:
            return
        # 如果开始时间和结束时间为空，则默认为当天时间
        start = start if start else datetime.now().date()
        end = end if end else datetime.now().date()
        self.prepare_analysis(start=start, end=end)
        # 获取时间范围数据
        date_range = list(
            pandas.date_range(start=start, end=end, freq="D").to_pydatetime()
        )
        trade_id = -1
        # 开始计算
        for date in date_range:
            if not webutils.is_trading_day(date):
                continue
            if trade_id == -1:
                trade_id = databox.trade(records)
            # 获取交易总览
            summary: DataFrame = databox.summary(trade_id=trade_id, date=date)
            # 取出参与交易的基金名称
            fund_names = databox.get_trade_fund_name(trade_id)
            self.assemble_data(summary=summary, fund_names=fund_names, today=date)
        databox.remove_trade_cache(trade_id)
        self.finalize_analysis()

    @abstractmethod
    def get_trade_analysis_record(self) -> List[Record]:
        """
        获取交易分析记录

        Returns:
            List[Record]: 交易记录列表

        """
        pass

    @abstractmethod
    def assemble_data(self, summary: DataFrame, fund_names: Tuple[str, ...], today):
        """
        组装数据的方法。

        Args:
            summary (DataFrame): 交易总览数据，包含多列数据，具体包含哪些列由子类实现决定。
            fund_names (Tuple[str, ...]): 需要组装的基金名称的元组。
            today (datetime.date): 当前日期，格式为datetime.date类型。

        Returns:
            无返回值。

        Raises:
            NotImplementedError: 这是一个抽象方法，子类必须实现该方法。

        """
        pass

    @abstractmethod
    def finalize_analysis(self):
        """
        抽象方法，用于完成交易分析报告的最终处理。

        Args:
            无参数。

        Returns:
            无返回值。

        Raises:
            NotImplementedError: 因为这是一个抽象方法，子类必须实现该方法，否则调用时会抛出此异常。

        """
        pass

    @abstractmethod
    def prepare_analysis(self, start, end):
        """
        准备分析所需的数据。

        Args:
            start (datetime.date): 分析的起始日期。
            end (datetime.date): 分析的结束日期。

        Returns:
            无返回值，该方法为抽象方法，具体实现应由子类完成。

        """
        pass

    def assemble_trade_analysis(
        self,
        summary_data: DataFrame,
        analysis_type=None,
        date: datetime = None,
        analysis_data: TradeAnalysisData = None,
        asset_id=None,
    ) -> TradeAnalysisData:
        """
        将交易总览数据转换为数据库对应的分析数据对象

        Args:
            summary_data (DataFrame): 交易总览数据，格式需要符合data_box对应的summary返回值，
                包含以下列【"基金名称","基金代码","当日净值","单位成本","持有份额","基金现值","基金总申购",
                        "历史最大占用","基金持有成本","基金分红与赎回","换手率","基金收益总额","投资收益率","内部收益率"】
            analysis_type (int, optional): 业务类型，默认为None。参考TransactionAnalysisTypeEnum。
            date (datetime, optional): 日期，默认为None。
            analysis_data (TransactionAnalysisData, optional): 数据库对应的分析数据对象，默认为None。
            asset_id (Any, optional): 资产ID，默认为None。

        Returns:
            TradeAnalysisData: 返回转换后的数据库对应的分析数据对象

        Raises:
            ValueError: 当summary_data为空或缺少总计行时抛出异常

        """
        # 检查DataFrame是否为空
        if summary_data is None or summary_data.empty:
            raise ValueError("交易总览数据不能为空")

        # 检查是否包含总计行
        if len(summary_data) == 0:
            raise ValueError("交易总览数据缺少总计行")

        trade_analysis_data: TradeAnalysisData = (
            TradeAnalysisData() if analysis_data is None else analysis_data
        )
        summary_data = summary_data.copy(deep=True)
        # 获取asset_id
        if (
            (
                analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID
                or analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID_TYPE
            )
            and trade_analysis_data.asset_id is None
            and asset_id is None
        ):
            # 获取基金代码
            fund_code = summary_data.iloc[0][webcons.XAFundSummaryColumns.FUND_CODE]
            asset_id = (
                AssetCode.query.filter(AssetCode.code_xq == fund_code).first().asset_id
            )
        name_dict = webcons.XAFundSummaryColumns.get_dict()
        # rename
        summary_data.rename(columns=name_dict, inplace=True)
        conversion_factors: Dict[str, int] = TradeAnalysisData.get_conversion_factor()
        # 填充数据
        for column, factor in conversion_factors.items():
            value = summary_data.iloc[0].get(column, None)
            if pd.isna(value):
                setattr(trade_analysis_data, column, None)
            else:
                setattr(trade_analysis_data, column, round(value * factor))
        trade_analysis_data.asset_id = asset_id
        trade_analysis_data.analysis_type = analysis_type
        trade_analysis_data.record_date = date if date is not None else datetime.now()
        return trade_analysis_data

    def assemble_grid_trade_analysis(
        self,
        analysis_data: TradeAnalysisData,
        grid_type_details: List[GridTypeDetail],
        records: List[Record] = None,
        date=None,
        grid_trade_analysis: GridTradeAnalysisData = None,
        business_type: int = None,
        *args,
        **kwargs,
    ) -> GridTradeAnalysisData:
        """
        分析网格交易记录

        Args:
            analysis_data (TradeAnalysisData): 交易分析数据
            grid_type_details (List[GridTypeDetail]): 网格类型详情列表
            records (List[Record], optional): 交易记录列表，默认为None。Defaults to None.
            date (datetime, optional): 日期，默认为当前日期。Defaults to None.
            grid_trade_analysis (GridTransactionAnalysisData, optional): 网格交易分析数据，默认为None。Defaults to None.

        Returns:
            GridTradeAnalysisData: 网格交易分析数据

        """
        # 初始化网格交易分析数据，继承TradeAnalysisData的所有字段
        if grid_trade_analysis is None:
            grid_trade_analysis = GridTradeAnalysisData(
                # 继承TradeAnalysisData的字段
                asset_id=analysis_data.asset_id,
                maximum_occupancy=analysis_data.maximum_occupancy,
                unit_cost=analysis_data.unit_cost,
                purchase_amount=analysis_data.purchase_amount,
                present_value=analysis_data.present_value,
                irr=analysis_data.irr,
                investment_yield=analysis_data.investment_yield,
                annualized_return=analysis_data.annualized_return,
                turnover_rate=analysis_data.turnover_rate,
                analysis_type=analysis_data.analysis_type,
                attributable_share=analysis_data.attributable_share,
                holding_cost=analysis_data.holding_cost,
                dividend=analysis_data.dividend,
                profit=analysis_data.profit,
                net_value=analysis_data.net_value,
                sub_analysis_type="grid_trade_analysis",
                # GridTradeAnalysisData特有字段
                business_type=business_type if business_type is not None else GridTradeAnalysisData.get_business_type_enum().GRID_STRATEGY_ANALYSIS.value,
                sell_times=0,
                estimate_maximum_occupancy=0,
                holding_times=0,
                up_sold_percent=0,
                down_bought_percent=0,
            )
        if date:
            grid_trade_analysis.record_date = date
        else:
            grid_trade_analysis.record_date = datetime.now()
        if not grid_type_details:
            return grid_trade_analysis
        # 根据网格ID查询网格类型详情数据
        detail_df = pd.DataFrame(
            GridTypeDetailDomainSchema().dump(grid_type_details, many=True)
        ).sort_values(by="gear", ascending=False)
        # 获取网格资产当前的净值，当计算总计数据时，net_value为0，需要做特殊处理
        net_value = analysis_data.net_value
        grid_trade_analysis.up_sold_percent, grid_trade_analysis.down_bought_percent = (
            self.get_bought_and_sell_percent(grid_type_details, net_value)
        )

        # 计算待出网次数
        grid_trade_analysis.holding_times = len(
            detail_df[detail_df["monitor_type"] == 1]
        )
        # 预计剩余最大占用金额
        grid_trade_analysis.estimate_maximum_occupancy = sum(
            detail_df.loc[detail_df["monitor_type"] == 0, "purchase_amount"]
        )
        if not records:
            return grid_trade_analysis
        # 计算已出网次数
        sell_enum_value = Record.get_record_directoin_enum().SELL.value
        grid_trade_analysis.sell_times = 0
        # 遍历records列表，计算已出网次数
        for record in records:
            if (
                record.transactions_direction == sell_enum_value
                and record.transactions_date <= grid_trade_analysis.record_date
            ):
                grid_trade_analysis.sell_times += 1
        return grid_trade_analysis

    def get_analysis_records_by_type(
        self,
        analysis_type: Union[int, TransactionAnalysisTypeEnum],
        record_key_id: int = None,
    ) -> List[Record]:
        """
        根据分析类型获取对应的交易记录

        Args:
            analysis_type (Union[int, TransactionAnalysisData.get_analysis_type_enum()]): 分析类型，支持以下几种类型：
                - TransactionAnalysisData.get_analysis_type_enum().AMOUNT：总体交易分析
                - TransactionAnalysisData.get_analysis_type_enum().GRID_TYPE：网格类型分析
                - TransactionAnalysisData.get_analysis_type_enum().GRID：网格分析
                - TransactionAnalysisData.get_analysis_type_enum().GRID_STRATEGY：网格策略分析
            record_key_id (int, optional): 记录关键ID，默认为None。
                - 当分析类型为网格类型分析时，需要指定网格类型ID。
                - 当分析类型为网格分析时，需要指定网格ID。
                - 当分析类型为网格策略分析时，需要指定策略ID。

        Returns:
            List[Record]: 返回符合条件的交易记录列表

        Raises:
            ValueError: 如果分析类型不支持或缺少必要的记录关键ID时，抛出异常
        """
        if analysis_type == TradeAnalysisData.get_analysis_type_enum().AMOUNT:
            return Record.query.order_by(Record.transactions_date.asc()).all()
        elif analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID_TYPE:
            if not record_key_id:
                raise ValueError("网格类型分析时必须指定网格类型ID")
            return (
                Record.query.join(GridTypeRecord, GridTypeRecord.record_id == Record.id)
                .filter(GridTypeRecord.grid_type_id == record_key_id)
                .order_by(Record.transactions_date.asc())
                .all()
            )
        elif analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID:
            if not record_key_id:
                raise ValueError("网格分析时必须指定网格ID")
            return (
                Record.query.join(GridTypeRecord, GridTypeRecord.record_id == Record.id)
                .join(GridType, GridType.id == GridTypeRecord.grid_type_id)
                .join(Grid, Grid.id == GridType.grid_id)
                .filter(Grid.id == record_key_id)
                .order_by(Record.transactions_date.asc())
                .all()
            )
        elif analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID_STRATEGY:
            return (
                Record.query.join(GridTypeRecord, GridTypeRecord.record_id == Record.id)
                .join(GridType, GridType.id == GridTypeRecord.grid_type_id)
                .join(Grid, Grid.id == GridType.grid_id)
                .order_by(Record.transactions_date.asc())
                .all()
            )
        else:
            raise ValueError("不支持的分析类型")

    @staticmethod
    def get_bought_and_sell_percent(
        grid_type_details: List[GridTypeDetail], net_value: Optional[int] = None
    ):
        """
        根据网格交易详情和净值计算买入和卖出的百分比变化。

        Args:
            grid_type_details (List[GridTypeDetail]): 网格交易详情列表。
            net_value (Optional[int], optional): 当前净值，默认为None。如果为None或小于等于0，则返回(None, None)。

        Returns:
            Tuple[Optional[Decimal], Optional[Decimal]]: 返回一个元组，包含卖出百分比和买入百分比。
                - 卖出百分比: 表示从当前净值到卖出触发价格所需的百分比变化，如果无法计算则返回None。
                - 买入百分比: 表示从当前净值到买入触发价格所需的百分比变化，如果无法计算则返回None。

        """
        if not grid_type_details or net_value is None or net_value <= 0:
            return None, None
        sell = bought = None
        detail_df = pd.DataFrame(
            GridTypeDetailDomainSchema().dump(grid_type_details, many=True)
        ).sort_values(by="gear", ascending=False)
        # 使用Decimal处理后面的除法小数点问题，计算出百分比
        net_value = Decimal(net_value)
        # 获取档位最小的卖出监控数据
        sell_df = detail_df[
            detail_df["monitor_type"]
            == GridTypeDetail.get_monitor_type_enum().SELL.value
        ].iloc[-1:]
        # 获取档位最大的买入监控数据
        buy_df = detail_df[
            detail_df["monitor_type"]
            == GridTypeDetail.get_monitor_type_enum().BUY.value
        ].iloc[:1]
        # numpy int64类型不能直接与Decimal进行比较
        # 计算距离卖出卖出需要的变化
        if not sell_df.empty:
            sell_price_decimal = Decimal(int(sell_df.iloc[0].trigger_sell_price))
            if int(sell_df.iloc[0].trigger_sell_price) > net_value > 0:
                sell = (sell_price_decimal - net_value) / net_value * 10000
        if not buy_df.empty:
            purchase_price_decimal = Decimal(int(buy_df.iloc[0].trigger_purchase_price))
            if net_value > purchase_price_decimal:
                bought = (net_value - purchase_price_decimal) / net_value * 10000
        return sell, bought


class AmountTransactionAnalysisService(TradeAnalysisService):

    def __init__(self, start=None, end=None):
        """
        初始化金额交易分析器类。

        Args:
            start (datetime.date, optional): 开始日期，默认为None，表示当前日期。
            end (datetime.date, optional): 结束日期，默认为None，表示当前日期。

        Properties
        strategy_id (int): 策略ID。
        """
        self.analysis_type: int = (
            TradeAnalysisData.get_analysis_type_enum().AMOUNT.value
        )
        self.start = start
        self.end = end
        self.date_trade_dict = {}
        self.update_trade_list: List[AmountTradeAnalysisData] = []

    def get_trade_analysis_record(self) -> List[Record]:

        return self.get_analysis_records_by_type(analysis_type=self.analysis_type)

    def assemble_trade_analysis(
        self,
        summary_data: DataFrame,
        analysis_type=None,
        date: datetime = None,
        analysis_data: AmountTradeAnalysisData = None,
        asset_id=None,
    ) -> AmountTradeAnalysisData:
        """
        将交易总览数据转换为AmountTradeAnalysisData对象

        Args:
            summary_data (DataFrame): 交易总览数据
            analysis_type (int, optional): 业务类型，默认为None
            date (datetime, optional): 日期，默认为None
            analysis_data (AmountTradeAnalysisData, optional): 数据库对应的分析数据对象，默认为None
            asset_id (Any, optional): 资产ID，默认为None

        Returns:
            AmountTradeAnalysisData: 返回转换后的AmountTradeAnalysisData对象
        """
        trade_analysis_data: AmountTradeAnalysisData = (
            AmountTradeAnalysisData() if analysis_data is None else analysis_data
        )
        summary_data = summary_data.copy(deep=True)
        # 获取asset_id
        if (
            (
                analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID
                or analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID_TYPE
            )
            and trade_analysis_data.asset_id is None
            and asset_id is None
        ):
            # 获取基金代码
            fund_code = summary_data.iloc[0][webcons.XAFundSummaryColumns.FUND_CODE]
            asset_id = (
                AssetCode.query.filter(AssetCode.code_xq == fund_code).first().asset_id
            )
        name_dict = webcons.XAFundSummaryColumns.get_dict()
        # rename
        summary_data.rename(columns=name_dict, inplace=True)
        conversion_factors: Dict[str, int] = (
            AmountTradeAnalysisData.get_conversion_factor()
        )
        # 填充数据，但跳过dividend_yield字段
        for column, factor in conversion_factors.items():
            if column == "dividend_yield":
                # 根据用户要求，不计算dividend_yield字段
                continue
            value = summary_data.iloc[0].get(column, None)
            if pd.isna(value):
                setattr(trade_analysis_data, column, None)
            else:
                setattr(trade_analysis_data, column, int(value * factor))
        trade_analysis_data.asset_id = asset_id
        trade_analysis_data.analysis_type = analysis_type
        trade_analysis_data.record_date = (
            date if date is not None else datetime.now().date()
        )
        # dividend_yield字段设置为None，不进行计算
        trade_analysis_data.dividend_yield = None
        return trade_analysis_data

    def assemble_data(self, summary: DataFrame, fund_names: Tuple[str, ...], today):
        # 检查summary是否为空或None
        if summary is None or summary.empty:
            raise ValueError("交易总览数据不能为空")

        # 检查fund_names是否为None
        if fund_names is None:
            raise TypeError("基金名称列表不能为None")

        # 检查fund_names是否为空
        if not fund_names:
            raise ValueError("基金名称列表不能为空")

        aggregation_summary = summary.loc[
            summary[databox.cons.XAFundSummaryColumns.FUND_NAME] == "总计"
        ]

        # 检查是否找到总计行
        if aggregation_summary.empty:
            raise ValueError("交易总览数据中缺少总计行")
        analysis_data = self.assemble_trade_analysis(
            summary_data=aggregation_summary,
            analysis_type=self.analysis_type,
            date=today,
            analysis_data=self.date_trade_dict.get(today, [None])[0],
        )
        self.update_trade_list.append(analysis_data)

    def finalize_analysis(self):
        if self.update_trade_list:
            db.session.bulk_save_objects(
                self.update_trade_list,return_defaults=True, update_changed_only=True
            )
            db.session.commit()

    def prepare_analysis(self, start, end):
        self.start = start
        self.end = end
        self.date_trade_dict = self.fetch_and_organize_trade_data()

    def fetch_and_organize_trade_data(self):
        trade_datas = (
            db.session.query(AmountTradeAnalysisData)
            .filter(
                AmountTradeAnalysisData.record_date >= self.start,
                AmountTradeAnalysisData.record_date <= self.end,
                AmountTradeAnalysisData.analysis_type == self.analysis_type,
            )
            .all()
        )
        date_trade_dict = {}
        for trade_data in trade_datas:
            date_trade_dict.setdefault(trade_data.record_date, []).append(trade_data)
        return date_trade_dict


class GridStrategyTransactionAnalysisService(TradeAnalysisService):

    def __init__(self, start=None, end=None):
        """
        初始化网格策略交易分析器类。

        Args:
            start (datetime.date, optional): 开始日期，默认为None，表示当前日期。
            end (datetime.date, optional): 结束日期，默认为None，表示当前日期。

        Properties
        strategy_id (int): 策略ID。
        """
        self.analysis_type: int = (
            TradeAnalysisData.get_analysis_type_enum().GRID_STRATEGY.value
        )
        self.start = start
        self.end = end
        self.date_trade_dict = {}
        self.grid_type_detail_dict = {}
        self.update_trade_list: List[GridTradeAnalysisData] = []

    def get_trade_analysis_record(self) -> List[Record]:
        return self.get_analysis_records_by_type(analysis_type=self.analysis_type)

    def assemble_data(self, summary: DataFrame, fund_names: Tuple[str, ...], today):
        # 检查summary是否为空或None
        if summary is None or summary.empty:
            raise ValueError("交易总览数据不能为空")

        # 检查fund_names是否为None
        if fund_names is None:
            raise TypeError("基金名称列表不能为None")

        # 检查fund_names是否为空
        if not fund_names:
            raise ValueError("基金名称列表不能为空")

        aggregation_summary = summary.loc[
            summary[databox.cons.XAFundSummaryColumns.FUND_NAME] == "总计"
        ]

        # 检查是否找到总计行
        if aggregation_summary.empty:
            raise ValueError("交易总览数据中缺少总计行")

        # 创建基础的TradeAnalysisData用于传递数据
        base_analysis_data = self.assemble_trade_analysis(
            summary_data=aggregation_summary,
            analysis_type=self.analysis_type,
            date=today,
            analysis_data=self.date_trade_dict.get(today, None),
        )

        grid_analysis_list: List[GridTradeAnalysisData] = []
        for grid_type_id, grid_type_detail_list in self.grid_type_detail_dict.items():
            grid_analysis = self.assemble_grid_trade_analysis(
                analysis_data=base_analysis_data,
                grid_type_details=grid_type_detail_list,
                records=self.records,
                date=today,
                business_type=GridTradeAnalysisData.get_business_type_enum().GRID_STRATEGY_ANALYSIS.value,
            )
            grid_analysis_list.append(grid_analysis)

        existing_trade_data = self.date_trade_dict.get(
            today,
            GridTradeAnalysisData(
                business_type=GridTradeAnalysisData.get_business_type_enum().GRID_STRATEGY_ANALYSIS.value,
                sub_analysis_type="grid_trade_analysis",
            ),
        )
        
        updated_grid_analysis = (
            GridTransactionAnalysisService.organize_grid_analysis_data(
                existing_data=existing_trade_data,
                analysis_data_list=grid_analysis_list,
                today=today,
                base_analysis_data=base_analysis_data,
            )
        )
        # 由于GridTradeAnalysisData继承了TradeAnalysisData，只需要保存GridTradeAnalysisData对象
        self.update_trade_list.append(updated_grid_analysis)

    def finalize_analysis(self):
        # 由于GridTradeAnalysisData现在继承自TradeAnalysisData，直接保存GridTradeAnalysisData对象
        if self.update_trade_list:
            db.session.bulk_save_objects(
                self.update_trade_list, return_defaults=True, update_changed_only=True
            )
            db.session.commit()

    def prepare_analysis(self, start, end):
        self.start = start
        self.end = end
        self.date_trade_dict = self.fetch_and_organize_trade_data()
        self.grid_type_detail_dict = self.fetch_and_fill_grid_type_details()

    def fetch_and_organize_trade_data(self):
        # 由于GridTradeAnalysisData现在继承自TradeAnalysisData，直接查询GridTradeAnalysisData
        trade_datas = (
            db.session.query(GridTradeAnalysisData)
            .filter(
                GridTradeAnalysisData.record_date >= self.start,
                GridTradeAnalysisData.record_date <= self.end,
                GridTradeAnalysisData.analysis_type == self.analysis_type,
            )
            .all()
        )
        date_trade_dict = {}
        for grid_trade in trade_datas:
            date = grid_trade.record_date
            date_trade_dict[date] = grid_trade  # 简化数据结构，直接存储GridTradeAnalysisData对象
        return date_trade_dict

    def fetch_and_fill_grid_type_details(self):
        """
        从数据库中获取网格类型详情，并将它们按网格类型ID分组，最后返回分组后的字典。

        Args:
            无

        Returns:
            dict: 包含网格类型ID作为键，网格类型详情列表作为值的字典。

        """
        grid_type_details = db.session.query(GridTypeDetail).all()
        detail_dict = {}
        for detail in grid_type_details:
            grid_type_detail_list = detail_dict.get(detail.grid_type_id, [])
            grid_type_detail_list.append(detail)
            detail_dict.update({detail.grid_type_id: grid_type_detail_list})
        return detail_dict


class GridTransactionAnalysisService(TradeAnalysisService):

    def __init__(self, grid_id: int, start=None, end=None):
        """
        初始化网格交易分析器类。

        Args:
            grid_id (int): 网格ID。
            start (datetime.date, optional): 开始日期，默认为None，表示当前日期。
            end (datetime.date, optional): 结束日期，默认为None，表示当前日期。

        Properties
        grid_id (int): 网格ID。
        """
        self.grid_id: int = grid_id
        self.analysis_type: int = TradeAnalysisData.get_analysis_type_enum().GRID.value
        self.start = start
        self.end = end
        self.grid: Grid = Grid.query.get(grid_id)
        self.date_trade_dict = {}
        self.update_trade_list: List[GridTradeAnalysisData] = []
        self.grid_type_detail_dict = {}

    def get_trade_analysis_record(self) -> List[Record]:
        return self.get_analysis_records_by_type(
            analysis_type=self.analysis_type, record_key_id=self.grid_id
        )

    def assemble_data(self, summary: DataFrame, fund_names: Tuple[str, ...], today):
        # 检查summary是否为空或None
        if summary is None or summary.empty:
            raise ValueError("交易总览数据不能为空")

        # 检查fund_names是否为None
        if fund_names is None:
            raise TypeError("基金名称列表不能为None")

        # 检查fund_names是否为空
        if not fund_names:
            raise ValueError("基金名称列表不能为空")

        for fund_name in fund_names:
            fund_summary = summary.loc[summary["基金名称"] == fund_name]

            # 检查是否找到对应基金的数据
            if fund_summary.empty:
                raise ValueError(f"交易总览数据中缺少基金 '{fund_name}' 的数据")

            # 创建基础的TradeAnalysisData用于传递数据
            base_analysis_data = self.assemble_trade_analysis(
                summary_data=fund_summary,
                analysis_type=self.analysis_type,
                date=today,
                analysis_data=self.date_trade_dict.get(today, [None])[0],
                asset_id=self.grid.asset_id,
            )

            # 遍历grid_type_detail_dict，获取每个网格类型对应的网格类型详情列表
            grid_analysis_list: List[GridTradeAnalysisData] = []
            for (
                grid_type_id,
                grid_type_detail_list,
            ) in self.grid_type_detail_dict.items():
                grid_analysis = self.assemble_grid_trade_analysis(
                    analysis_data=base_analysis_data,
                    grid_type_details=grid_type_detail_list,
                    records=self.records,
                    date=today,
                    business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
                )
                # 设置grid_id以建立关联关系
                grid_analysis.grid_id = self.grid_id
                grid_analysis_list.append(grid_analysis)

            existing_trade_data = self.date_trade_dict.get(
                today,
                [
                    GridTradeAnalysisData(
                        business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
                        sub_analysis_type="grid_trade_analysis",
                        asset_id=self.grid.asset_id,
                    )
                ],
            )[0]
            updated_grid_analysis = self.organize_grid_analysis_data(
                existing_data=existing_trade_data,
                analysis_data_list=grid_analysis_list,
                today=today,
                base_analysis_data=base_analysis_data,
            )
            # 设置grid_id以建立关联关系
            updated_grid_analysis.grid_id = self.grid_id
            self.update_trade_list.append(updated_grid_analysis)

    def finalize_analysis(self):
        # 由于GridTradeAnalysisData现在继承自TradeAnalysisData，直接保存GridTradeAnalysisData对象
        if self.update_trade_list:
            db.session.bulk_save_objects(
                self.update_trade_list, return_defaults=True, update_changed_only=True
            )
            db.session.commit()

    def prepare_analysis(self, start, end):
        self.start = start
        self.end = end
        self.date_trade_dict = self.fetch_and_organize_trade_data()
        self.fetch_and_fill_grid_type_details()

    @staticmethod
    def organize_grid_analysis_data(
        existing_data: GridTradeAnalysisData,
        analysis_data_list: List[GridTradeAnalysisData],
        today,
        base_analysis_data: TradeAnalysisData = None,
    ) -> GridTradeAnalysisData:
        """
        组织网格交易分析数据，并返回汇总后的数据。

        Args:
            existing_data (GridTradeAnalysisData): 现有的网格交易分析数据对象，如果为None，则创建一个新的GridTransactionAnalysisData对象作为汇总数据。
            analysis_data_list (List[GridTransactionAnalysisData]): 网格交易分析数据列表，包含多个GridTransactionAnalysisData对象。
            today (datetime.date): 今天的日期。

        Returns:
            GridTradeAnalysisData: 汇总后的网格交易分析数据对象。

        """
        # 如果existing_data是新创建的对象且提供了base_analysis_data，复制基础字段
        if base_analysis_data:
            # 复制TradeAnalysisData的所有基础字段
            existing_data.asset_id = base_analysis_data.asset_id
            existing_data.analysis_type = base_analysis_data.analysis_type
            existing_data.maximum_occupancy = base_analysis_data.maximum_occupancy
            existing_data.unit_cost = base_analysis_data.unit_cost
            existing_data.purchase_amount = base_analysis_data.purchase_amount
            existing_data.present_value = base_analysis_data.present_value
            existing_data.irr = base_analysis_data.irr
            existing_data.investment_yield = base_analysis_data.investment_yield
            existing_data.annualized_return = base_analysis_data.annualized_return
            existing_data.turnover_rate = base_analysis_data.turnover_rate
            existing_data.attributable_share = base_analysis_data.attributable_share
            existing_data.holding_cost = base_analysis_data.holding_cost
            existing_data.dividend = base_analysis_data.dividend
            existing_data.profit = base_analysis_data.profit
            existing_data.net_value = base_analysis_data.net_value

        # 累加GridTradeAnalysisData特有字段
        total_sell_times = 0
        total_estimate_maximum_occupancy = 0
        total_holding_times = 0
        min_up_sold_percent = None
        min_down_bought_percent = None
        
        # 遍历数据列表，累加和更新相关字段
        for data in analysis_data_list:
            total_sell_times += data.sell_times
            total_estimate_maximum_occupancy += data.estimate_maximum_occupancy
            total_holding_times += data.holding_times
            if data.up_sold_percent is not None and (
                min_up_sold_percent is None
                or min_up_sold_percent > data.up_sold_percent
            ):
                min_up_sold_percent = data.up_sold_percent
            if data.down_bought_percent is not None and (
                min_down_bought_percent is None
                or min_down_bought_percent > data.down_bought_percent
            ):
                min_down_bought_percent = data.down_bought_percent
        
        # 将累加结果赋值给existing_data对象
        existing_data.sell_times = total_sell_times
        existing_data.estimate_maximum_occupancy = total_estimate_maximum_occupancy
        existing_data.holding_times = total_holding_times
        existing_data.up_sold_percent = min_up_sold_percent
        existing_data.down_bought_percent = min_down_bought_percent
        existing_data.record_date = today
        return existing_data

    def fetch_and_organize_trade_data(self):
        # 由于GridTradeAnalysisData现在继承自TradeAnalysisData，直接查询GridTradeAnalysisData
        trade_datas = (
            db.session.query(GridTradeAnalysisData)
            .filter(
                GridTradeAnalysisData.grid_id == self.grid_id,
                GridTradeAnalysisData.record_date >= self.start,
                GridTradeAnalysisData.record_date <= self.end,
                GridTradeAnalysisData.analysis_type == self.analysis_type,
            )
            .all()
        )
        date_trade_dict = {}
        for grid_trade in trade_datas:
            date = grid_trade.record_date
            date_trade_dict[date] = [grid_trade]  # 简化数据结构
        return date_trade_dict

    def fetch_and_fill_grid_type_details(self):
        grid_type_details = (
            db.session.query(GridTypeDetail)
            .filter(GridTypeDetail.grid_id == self.grid_id)
            .all()
        )
        for detail in grid_type_details:
            grid_type_detail_list = self.grid_type_detail_dict.get(
                detail.grid_type_id, []
            )
            grid_type_detail_list.append(detail)
            self.grid_type_detail_dict.update(
                {detail.grid_type_id: grid_type_detail_list}
            )


class GridTypeTransactionAnalysisService(TradeAnalysisService):

    def __init__(self, grid_type_id: int, start=None, end=None):
        """
        初始化网格类型分析器类。

        Args:
            grid_type_id (int): 网格类型ID。
            start (datetime.date, optional): 开始日期，默认为None，表示当前日期。
            end (datetime.date, optional): 结束日期，默认为None，表示当前日期。

        Properties:
            grid_type_id (int): 网格类型ID。
            analysis_type (int): 分析类型，默认为网格类型分析。
            start (datetime.date): 开始日期。
            end (datetime.date): 结束日期。
            grid_type (GridType): 网格类型对象。
            date_trade_dict (dict): 日期与交易数据的字典，键为日期，值为GridTradeAnalysisData对象。
            update_trade_list (List[GridTradeAnalysisData]):
             待更新的交易数据列表，包含网格交易分析数据。
        """
        super().__init__()  # 调用父类的__init__方法，初始化records属性
        self.grid_type_id: int = grid_type_id
        self.analysis_type: int = (
            TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value
        )
        self.start = start
        self.end = end
        self.grid_type: GridType = self._get_grid_type(grid_type_id)
        self.date_trade_dict = {}
        self.update_trade_list: List[GridTradeAnalysisData] = []
        self.grid_type_details = []

    def _get_grid_type(self, grid_type_id: int) -> GridType:
        """
        根据网格类型ID获取网格类型对象

        Args:
            grid_type_id (int): 网格类型ID

        Returns:
            GridType: 网格类型对象

        Raises:
            ValueError: 当grid_type_id为None或获取失败时抛出异常
        """
        if grid_type_id is None:
            raise ValueError("网格类型ID不能为None")

        grid_type = GridType.query.get(grid_type_id)
        if grid_type is None:
            raise ValueError(f"未找到ID为{grid_type_id}的网格类型")

        return grid_type

    def prepare_analysis(self, start, end):
        self.start = start
        self.end = end
        self.date_trade_dict = self.fetch_and_organize_trade_data()
        self.grid_type_details = self.fetch_grid_type_detail()

    def fetch_and_organize_trade_data(self):
        """
        根据网格类型id、起始日期、结束日期和分析类型，从数据库中查询并整理交易数据。

        Args:
            无

        Returns:
            dict: 包含日期与交易数据的字典，键为日期，值为GridTradeAnalysisData对象。

        """
        # 构建查询条件
        query = db.session.query(GridTradeAnalysisData).filter(
            GridTradeAnalysisData.grid_type_id == self.grid_type_id,
            GridTradeAnalysisData.analysis_type == self.analysis_type,
        )

        # 只有当start和end不为None时才添加日期过滤条件
        if self.start is not None:
            query = query.filter(GridTradeAnalysisData.record_date >= self.start)
        if self.end is not None:
            query = query.filter(GridTradeAnalysisData.record_date <= self.end)

        trade_datas = query.all()

        date_trade_dict = {}
        for grid_trade in trade_datas:
            date = grid_trade.record_date
            date_trade_dict[date] = grid_trade
        return date_trade_dict

    def fetch_grid_type_detail(self):
        return (
            db.session.query(GridTypeDetail)
            .filter(GridTypeDetail.grid_type_id == self.grid_type_id)
            .all()
        )

    def get_trade_analysis_record(self) -> List[Record]:
        """
        获取网格类型的交易分析记录。

        Args:
            无参数。

        Returns:
            List[Record]: 返回网格类型的交易分析记录列表。

        """
        return self.get_analysis_records_by_type(
            analysis_type=TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value,
            record_key_id=self.grid_type_id,
        )

    def assemble_data(self, summary: DataFrame, fund_names: Tuple[str, ...], today):
        """ "组装交易分析数据

        Args:
            summary (DataFrame): 交易总览数据，包含基金名称、基金代码等信息
            fund_names (Tuple[str, ...]): 基金名称元组
            today (datetime.date): 当前日期

        Returns:
            None

        说明：
            遍历基金名称元组，对每一个基金名称，分别调用assemble_grid_trade_analysis方法，
            将返回的网格交易分析数据添加到self.update_trade_list中。
        """
        # 检查fund_names是否为None
        if fund_names is None:
            raise TypeError("基金名称列表不能为None")

        # 检查fund_names是否为空
        if not fund_names:
            raise ValueError("基金名称列表不能为空")

        for fund_name in fund_names:
            # 由于GridTradeAnalysisData现在继承自TradeAnalysisData，直接使用现有数据或创建新的GridTradeAnalysisData
            existing_grid_trade_data = self.date_trade_dict.get(today, None)

            # 组装基础分析数据到GridTradeAnalysisData中
            base_analysis_data = self.assemble_trade_analysis(
                summary_data=summary.loc[summary["基金名称"] == fund_name],
                analysis_type=self.analysis_type,
                date=today,
                analysis_data=existing_grid_trade_data,
                asset_id=self.grid_type.asset_id,
            )

            # 组装网格交易分析数据，传入基础分析数据
            grid_trade_analysis = self.assemble_grid_trade_analysis(
                date=today,
                analysis_data=base_analysis_data,
                grid_trade_analysis=existing_grid_trade_data,
                grid_type_details=self.grid_type_details,
                records=self.records,
                business_type=GridTradeAnalysisData.get_business_type_enum().GRID_TYPE_ANALYSIS.value,
            )
            # 设置网格类型ID和网格ID
            grid_trade_analysis.grid_type_id = self.grid_type_id
            grid_trade_analysis.grid_id = self.grid_type.grid_id

            self.update_trade_list.append(grid_trade_analysis)

    def finalize_analysis(self):
        """
        完成交易分析。

        Args:
            无

        Returns:
            无
        """
        # 由于GridTradeAnalysisData现在继承自TradeAnalysisData并包含grid_type_id字段，直接保存GridTradeAnalysisData
        if self.update_trade_list:
            db.session.bulk_save_objects(
                self.update_trade_list, return_defaults=True, update_changed_only=True
            )
            db.session.commit()


def get_records_date_range(
    record_list: List[Record], start=None, end=None
) -> Optional[Tuple[datetime.date, datetime.date]]:
    """
    从记录列表中获取指定日期范围内的最早和最晚交易日期。

    Args:
        record_list (List[Record]): 交易记录列表。
        start (datetime.date, optional): 开始日期，默认为None。如果为None，则使用记录列表中的最早日期。
        end (datetime.date, optional): 结束日期，默认为None。如果为None，则使用当前日期。

    Returns:
        Optional[Tuple[datetime.date, datetime.date]]: 如果记录列表非空，则返回指定日期范围内的最早和最晚交易日期；否则返回None。
    """
    if not record_list:
        return None
    record_start = min(record.transactions_date for record in record_list)
    if start is None or start < record_start:
        return_start = record_start
    else:
        return_start = start
    if end is not None:
        return_end = end
    else:
        return_end = datetime.today().date()
    return return_start, return_end


def trade_analysis_all_the_time(
    start: Union[datetime, str] = None, end: Union[datetime, str] = None
):
    """
    对所有类型的交易进行实时分析。

    对所有网格类型、网格、网格策略以及所有策略的交易记录进行实时分析。

    Args:
        start (Union[datetime, str], optional): 分析的开始时间，默认为None。
                如果为datetime类型，则直接使用该时间；如果为str类型，则尝试将其转换为datetime类型。
        end (Union[datetime, str], optional): 分析的结束时间，默认为None。
                如果为datetime类型，则直接使用该时间；如果为str类型，则尝试将其转换为datetime类型。

    Returns:
        None

    """
    start = webutils.convert_date(start)
    end = webutils.convert_date(end)
    # 网格类型交易分析
    grid_type_list: List[GridType] = GridType.query.all()
    for grid_type in grid_type_list:
        grid_type_service: TradeAnalysisService = GridTypeTransactionAnalysisService(
            grid_type_id=grid_type.id
        )
        records: List[Record] = grid_type_service.get_trade_analysis_record()
        analysis_start, analysis_end = get_records_date_range(
            records, start=start, end=end
        )
        grid_type_service.trade_analysis(start=analysis_start, end=analysis_end)
    # 网格交易分析
    grid_list: List[Grid] = Grid.query.all()
    for grid in grid_list:
        grid_service: TradeAnalysisService = GridTransactionAnalysisService(
            grid_id=grid.id
        )
        records: List[Record] = grid_service.get_trade_analysis_record()
        analysis_start, analysis_end = get_records_date_range(
            records, start=start, end=end
        )
        grid_service.trade_analysis(start=analysis_start, end=analysis_end)
    # 网格策略分析
    grid_strategy_trade_service: TradeAnalysisService = (
        GridStrategyTransactionAnalysisService()
    )
    records: List[Record] = grid_strategy_trade_service.get_trade_analysis_record()
    analysis_start, analysis_end = get_records_date_range(records, start=start, end=end)
    grid_strategy_trade_service.trade_analysis(start=analysis_start, end=analysis_end)
    # 所有策略交易分析
    trade_analysis_service: TradeAnalysisService = AmountTransactionAnalysisService()
    records: List[Record] = trade_analysis_service.get_trade_analysis_record()
    analysis_start, analysis_end = get_records_date_range(records, start=start, end=end)
    trade_analysis_service.trade_analysis(start=analysis_start, end=analysis_end)
