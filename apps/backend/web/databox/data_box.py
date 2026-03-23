from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Union, Optional

from pandas import DataFrame

from web.common.cache import cache
from web.common.cons import webcons
from web.common.enum.asset_enum import AssetTypeEnum
from web.common.enum.common_enum import MarketEnum
from web.common.enum.databox.databox_enum import DataBoxAdapterEnum, DataBoxEnums
from web.common.utils.WebUtils import web_utils
from web.databox.adapter.data.AkShareAdapter import AkShareAdapter
from web.databox.adapter.data.DataBoxDataAdapter import DataBoxDataAdapter
from web.databox.adapter.data.TorxiongAdapter import TorxiongAdapter
from web.databox.adapter.data.xa_data_adapter import XaDataAdapter
from web.databox.adapter.data.xa_service import XaServiceAdapter
from web.databox.enum.IndicatorEnum import IndicatorEnum
from web.databox.interfaces.convertible_bond_interface import ConvertibleBondIssuanceInterface
from web.databox.models.dividend_yield import IndexDividendYieldData
from web.databox.models.dto.convertible_bond_issuance import ConvertibleBondIssuanceData
from web.databox.models.fund import DataBoxFundInfo
from web.databox.service.adapter_service import AdapterService
from web.databox.service.convertible_bond_service import ConvertibleBondService
from web.databox.service.index_valuation_service import IndexValuationService
from web.services.system.system_token_service import system_token_service
from web.models import db
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.models.asset.AssetHoldingData import AssetHoldingDataDTO
from web.models.asset.asset import AssetStockDTO, AssetCurrentDTO
from web.models.asset.asset_code import AssetCode
from web.models.record.record import Record
from web.weblogger import error


class DataBox:
    xa_adapter: XaDataAdapter
    torxiong_adapter: TorxiongAdapter
    akshare_adapter: AkShareAdapter
    adapter: DataBoxDataAdapter
    adapter_service: AdapterService
    index_valuation_service: IndexValuationService
    convertible_bond_service: ConvertibleBondService

    def __init__(self, asset_id: int = None):
        """
        数据盒子：数据获取类，专用于与外部数据打交道，比如获取或更新基金数据，此类需要从外部获取的数据统一使用此接口
            内部维护了多个数据适配器，在外部调用接口时，自动判断应该使用什么数据来源。
            尽管使用了多个数据适配器，但是从设计意图上来说，希望接口返回的结果是不变的。
        Args:
            asset_id: 对应的证券数据ID，可以为空，为空时不能直接调用获取数据等接口

        Returns:

        """
        self.lock = threading.RLock()
        if asset_id:
            asset_code: AssetCode = AssetCode.query.filter(AssetCode.asset_id == asset_id).first()
            self.xa_adapter = XaDataAdapter(code_ttjj=asset_code.code_ttjj, code_xq=asset_code.code_xq)
        else:
            self.xa_adapter = XaDataAdapter()
        self.torxiong_adapter = TorxiongAdapter()
        self.akshare_adapter = AkShareAdapter()
        self.xa_service = XaServiceAdapter()
        self.adapter = self.xa_adapter
        self.cons = webcons
        self.enums = DataBoxEnums()
        # 初始化适配器服务，传入现有的适配器实例
        external_adapters = {
            DataBoxAdapterEnum.XA.value: self.xa_adapter,
            DataBoxAdapterEnum.TORXIONG.value: self.torxiong_adapter,
            DataBoxAdapterEnum.AKSHARE.value: self.akshare_adapter,
            DataBoxAdapterEnum.XA_SERVICE.value: self.xa_service
        }
        self.adapter_service = AdapterService(external_adapters)
        # 初始化指数估值服务
        self.index_valuation_service = IndexValuationService(self.adapter_service)
        # 初始化可转债发行服务
        self.convertible_bond_service = ConvertibleBondService(self.adapter_service)

    def init_app(self, app):
        is_lite_runtime = app.config.get("_config_name") == "lite" or app.config.get("ENV") == "lite"
        if is_lite_runtime:
            try:
                xq_token = system_token_service.get_xq_token()
            except Exception as exc:
                error(f"lite databox 初始化时读取 SQLite token 失败: {exc}", exc_info=True)
                return
            if xq_token:
                self.xa_adapter.init_adapter(xq_token)
                self.xa_service.init_adapter(xq_token)
            return

        redis_client = cache.get_redis_client()
        xq_token = redis_client.get(webcons.RedisKey.XQ_TOKEN)
        if xq_token:
            xq_token = json.loads(xq_token)
            self.xa_adapter.init_adapter(xq_token)
            self.xa_service.init_adapter(xq_token)

    def net_accessible(self, code_type: str, code: str) -> Union[bool, str]:
        """
        检查指定代码类型是否可通过网络访问，并返回资源名称。

        Args:
            code_type (str): 代码类型，例如 'XQ', 'INDEX', 'TTJJ' 等。
            code (str): 要检查的代码，例如股票代码或基金代码。

        Returns:
            Union[bool, str]: 如果代码类型对应的资源可通过网络访问，则返回 (True, 资源名称) 的元组；
                             否则返回 (False, None)。

        Raises:
            不直接抛出异常，而是通过内部方法处理可能发生的异常。

        注意:
            - 如果资源可访问，将同时返回资源名称。
            - 如果资源不可访问，将返回 False 和 None。
        """
        try:
            if self.enums.codeTypeEnum.XQ.value == code_type or self.enums.codeTypeEnum.INDEX.value == code_type:
                asset_current = self.xa_service.get_rt(code)
                return True, asset_current.name
            elif self.enums.codeTypeEnum.TTJJ.value == code_type:
                fundinfo = self.xa_service.fundinfo(code)
                return True, fundinfo.name
        except Exception as e:
            error(f"Code {code} is not accessible，e : {e}", exc_info=True)
        return False, None

    def get_cb_issuance_cninfo(self, start_date, end_date):
        """
        获取可转债发行情况（巨潮资讯 bond_cov_issue_cninfo）。

        参数可为 date 或字符串（支持 YYYY-MM-DD / YYYYMMDD），内部统一转换为 YYYYMMDD。
        返回 pandas.DataFrame 原始数据，字段与 AkShare 保持一致，便于后续自定义处理。
        """
        try:
            return self.akshare_adapter.get_cb_issuance_cninfo(start_date=start_date, end_date=end_date)
        except Exception as e:
            error(f"获取可转债发行数据失败：{e}", exc_info=True)
            from pandas import DataFrame
            return DataFrame()

    def get_cb_issuance_list(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        source: Optional[str | DataBoxAdapterEnum] = None,
        market: Optional[MarketEnum] = None,
    ) -> List[ConvertibleBondIssuanceData]:
        """
        获取时间区间内的可转债发行列表（返回 AkShare 原始 DataFrame）。
        优先通过适配器服务选择 provider，再由服务层统一执行；当指定 source 严格模式时，不具备能力将抛出异常。
        """
        adapter = self.adapter_service.get_adapter_by_capability(
            interface_class=ConvertibleBondIssuanceInterface,
            market=market,
            preferred=source,
        )
        return self.convertible_bond_service.list_issuance(
            start_date=start_date,
            end_date=end_date,
            market=market,
            source=source if source is not None else DataBoxAdapterEnum.AKSHARE,
            provider=adapter,
        )

    def set_token(self, key: str, token: Dict):
        """
        设置指定key的token

        Args:
            key (str): 要设置的token的key
            token (Dict): 要设置的token信息

        Returns:
            无

        """
        if key == webcons.DataBoxTokenKey.XQ_TOKEN:
            self.xa_adapter.get_core().universal.set_token(token)
            self.xa_service.xa.universal.set_token(token)

    def get_token(self, key: str) -> Dict:
        """
        获取指定key的token

        Args:
            key (str): 要获取的token的key

        Returns:
            Dict: 指定key的token信息，如果获取失败，返回空字典{}

        """
        if key == webcons.DataBoxTokenKey.XQ_TOKEN:
            try:
                token = self.xa_adapter.get_core().universal.get_token()
                return token
            except Exception:
                error("获取token失败，可能是因为没有设置", exc_info=True)
                return {}

    @classmethod
    def get_adapter_enum(cls):
        return DataBoxAdapterEnum

    def fund_info(self, code: str) -> Optional[DataBoxFundInfo]:
        """
        根据基金代码获取基金信息。

        Args:
            code (str): 基金代码，用于查询基金信息。

        Returns:
            Optional[DataBoxFundInfo]: 如果查询成功，返回一个包含基金价格、收益率和费用信息的 DataBoxFundInfo 对象；
                                       如果查询失败，则返回 None。

        Raises:
            不直接抛出异常，但如果在查询过程中发生错误，将记录错误信息并返回 None。

        注意:
            - 此方法通过调用 xa_service 的 fundinfo 方法来获取基金信息。
            - 如果 fundinfo 方法抛出异常，将捕获该异常并记录错误信息，同时返回 None。
        """
        try:
            fund_info = self.xa_service.fundinfo(code)
            return DataBoxFundInfo(price=fund_info.price, rate=fund_info.rate, fee_info=fund_info.feeinfo)
        except Exception:
            error(f"获取{code}的基金信息失败")
        return None



    def get_stock_holdings(self, asset_code: AssetCode, year: int, quarter: int) -> List[AssetHoldingDataDTO]:
        """
        获取基金的持仓数据，因为数据接口能力限制，暂时无法获取FOF基金
        Args:
            asset_code (AssetCode): 资产代码 用于获取天天基金代码， 天天基金代码不能为空
            year (int): 年份
            quarter (int):  季度

        Returns:
            List[AssetHoldingDataDTO] : 返回持仓数据列表，如果获取失败，返回空列表[]
        """
        if asset_code.code_ttjj is None:
            error('调用持仓接口失败，天天基金代码不存在，asset id : %d ' % asset_code.asset_id)
            raise ValueError('Invalid asset_code, code_ttjj is not existed')
        return self.xa_adapter.get_stock_holdings(asset_code.code_ttjj, year, quarter)

    def get_rt(self, code: str, source: None | str | DataBoxDataAdapter = None) -> Union[AssetCurrentDTO, None]:
        """
        根据代码获取实时数据

        Args:
            source (None | str | DataBoxDataAdapter, optional): 数据来源，用于区分数据来源。如果为空，则默认为xa。可以是数据源适配器的实例或数据源的名称。
            code (str): 代码，表示某种资产，比如SZ000001(A股)，512980（A股），PBF（美股）等。

        Returns:
            Union[AssetCurrentDTO, None]: 返回实时数据，如果获取失败，返回None。

        Raises:
            ValueError: 获取不到数据时（比如token失效），会抛出数据处理异常，因为远程服务返回非预期的数据。
        """
        if source is not None:
            if isinstance(source, DataBoxDataAdapter):
                return source.get_rt(code=code)
            else:
                adapter: DataBoxDataAdapter = self.adapter_service.get_adapter(source)
                if adapter is not None:
                    return adapter.get_rt(code=code)
                else:
                    error(f"Adapter {source} is not available")
                    return None
        if len(code) == 6 and code.isdigit():
            return self.torxiong_adapter.get_rt(code=code)
        return self.xa_adapter.get_rt(code=code)

    def get_adapter(self) -> DataBoxDataAdapter:
        return self.xa_adapter

    def get_core(self):
        return self.xa_adapter.get_core()

    def trade(self, records: List[Record]) -> int | str:
        """
            交易分析接口，调用适配器进行交易，并将结果存储到数据盒子缓存中，返回该次交易的ID号，通过该交易缓存ID号可以获取到对应的交易数据，
        比如查看某类交易在某天的交易概述，可以通过该ID获取
            注：1.交易数据应该根据日期升序
               2.如果是场内交易，一般可以实时获取到交易数据，因此可以立刻获取当前的交易分析结果
        Args:
            records: 交易记录，格式对应数据库模型

        Returns:
            返回该次交易的交易ID，此后可以通过该ID获取相关数据，如果交易分析失败，返回-1
        """
        with self.lock:
            try:
                cache_id = self.xa_adapter.trade(records)
                return cache_id
            except Exception as e:
                error('调用交易接口失败 ， 请检查数据， 错误信息: %s' % e, exc_info=True)
                return -1

    def remove_trade_cache(self, trade_id: int):
        """
        删除交易缓存，如果不存在，则不做任何操作
        Args:
            trade_id: 交易缓存ID
        """
        if trade_id in self.xa_adapter.trade_cache.keys():
            self.xa_adapter.trade_cache.pop(trade_id)

    def get_trade_fund_name(self, trade_id: int) -> tuple[str, ...]:
        """
            根据交易ID从缓存中获取交易数据的基金名称，以元组的形式返回，不包含总计数据
        抛出异常：当trade_id对应的交易缓存数据不存在时，将抛出交易分析异常：WebAnalyzerException
        Args:
            trade_id: 交易缓存ID
        Returns:
            基金名称数据元组，如：('华宝油气LOF')
        """
        return self.xa_adapter.get_trade_fund_name(trade_id=trade_id)

    def summary(self, trade_id: int, date=None) -> DataFrame:
        """
        获取交易总览，如果不指定日期，则默认查询当天的交易总览，如果交易数据缓存不存在，抛出异常
        Args:
            trade_id: not None，交易数据缓存ID
            date:   交易总览日期，可以是一个日期格式的字符串

        Returns:
            交易总览数据，包含多列，其中一列为总计数据，其他列为交易基金对应的总览数据
            包含字段：【"基金名称","基金代码","当日净值","单位成本","持有份额","基金现值","基金总申购",
            "历史最大占用","基金持有成本","基金分红与赎回","换手率","基金收益总额","投资收益率","内部收益率"】
        """
        return self.xa_adapter.summary(trade_id=trade_id, date=date)

    def set_asset(self, asset_id: int):
        asset_code: AssetCode = AssetCode.query.filter(AssetCode.asset_id == asset_id).first()
        self.xa_adapter = XaDataAdapter(code_ttjj=asset_code.code_ttjj, code_xq=asset_code.code_xq)

    def fetch_all_stock_asset(self) -> List[AssetStockDTO]:
        """
        方法内容：调用torxiong适配器，获取所有A股股票代码和名称数据
        设计目的：在更新持仓数据时，需要知道对应仓位的代码和名称，由于持仓数据格式的原因，无法通过get_rt获取，其他接口可以获取持仓数据，但有次数限制
            因此设计一个接口，用于获取所有股票的代码和名称，以便在更新持仓数据时使用可以用到
        Returns:
            股票数据列表
        """
        return self.torxiong_adapter.fetch_all_stock_asset()

    def fetch_online_daily_data(self, code: str = None, asset_id: int = None, asset_code: AssetCode = None,
                                start_date: datetime = None, end_date: datetime = None) -> Optional[DataFrame]:
        """
        从在线数据源获取指定资产的日线数据。

        Args:
            code (str, optional): 资产代码。如果提供，将直接使用此代码获取数据。
            asset_id (int, optional): 资产ID。用于查询资产代码。
            asset_code (AssetCode, optional): 资产代码对象。如果提供，将使用其`code_xq`属性获取数据。
            start_date (datetime, optional): 开始日期。
            end_date (datetime, optional): 结束日期。

        Returns:
            Optional[DataFrame]: 包含指定资产日线数据的DataFrame对象，如果获取成功则返回；如果获取失败，则返回None。

        Raises:
            ValueError:
                - 如果未提供有效的资产代码（code）或资产ID（asset_id）和资产代码对象（asset_code）同时为空。
                - 如果提供的asset_id无效，无法查询到对应的资产代码。

        注意事项:
            - 如果同时提供了code、asset_id和asset_code，将优先使用code获取数据。
            - 如果未提供code，但提供了asset_id，将使用asset_id查询对应的asset_code，并使用asset_code的code_xq属性获取数据。
            - 如果在数据获取过程中发生异常，将捕获异常并记录错误信息，同时返回None。
        """
        try:
            if code:
                return self.xa_service.get_daily(code, start_date, end_date)
            if not (asset_id or asset_code):
                raise ValueError('asset_id and asset_code can not be None at the same time')
            # 如果asset_id不为空，查询asset_code
            if asset_id is not None:
                asset_code = AssetCode.query.filter(AssetCode.asset_id == asset_id).first()
            if asset_code is None or asset_code.code_xq is None:
                raise ValueError("asset_id is invalid")
            return self.xa_service.get_daily(asset_code.code_xq, start_date, end_date)
        except Exception as e:
            error(f"获取日线数据失败，错误信息：{e}", exc_info=True)
            return None

    def fetch_daily_data(self, asset_id: int = None, asset_code: AssetCode = None,
                         start_date: datetime = None, end_date: datetime = None) -> List[AssetFundDailyData]:
        """
        方法内容：当确定数据库没有该数据时，调用此方法，此方法会从网络中获取基金的日线数据，如果不指定开始日期和结束日期，则默认查询当天的日线数据 \n
        设计目的：可以用于更新基金的日线数据 \n
        方法实现：获取天天基金代码，调用xa获取基金净值，获取雪球代码，调用xa.get_daily获取基金日线数据，封装后返回 \n
        Args:
            asset_id (int): 可选，资产ID,与asset_code不能同时为空，此参数不会改变data_box初始化时设置的asset_id
            asset_code (AssetCode): 可选资产代码
            start_date (datetime): 可选，开始日期，只能与end_date同时为空
            end_date (datetime): 可选，结束日期，只能与start_date同时为空

        Returns:
            基金日线数据
        """
        if asset_id is None and asset_code is None:
            raise ValueError('asset_id and asset_code can not be None at the same time')
        # 如果asset_id不为空，查询asset_code
        if asset_id is not None:
            asset_code = AssetCode.query.filter(AssetCode.asset_id == asset_id).first()
        # 如果start_date和end_date都为空，则默认使用当天的日期
        if start_date is None and end_date is None:
            start_date = end_date = datetime.now()
        # 使用xa_adapter的fetch_daily_data方法，该方法会处理重复数据问题
        try:
            return self.xa_adapter.fetch_daily_data(asset_code=asset_code, start_date=start_date, end_date=end_date)
        except AttributeError:
            # 如果xa_adapter没有fetch_daily_data方法(比如在旧版本)，则回退到使用get_daily方法
            error("xa_adapter没有fetch_daily_data方法，回退到使用get_daily方法")
            return self.xa_adapter.get_daily(asset_code=asset_code, start_date=start_date, end_date=end_date)

    def get_daily_data(self, asset_id: int = None, asset_code: AssetCode = None,
                       start_date: datetime = None, end_date: datetime = None) -> List[AssetFundDailyData]:
        """
        方法内容:获取基金的日线数据，如果不指定日期，则默认查询当天的日线数据，此方法会先从数据库中查询，如果数据库中没有，则调用fetch_daily_data方法获取
                如果不确定数据库中是否有数据，建议调用此方法，此方法会自动更新数据库start_date - end_date的缺失数据
        设计目的：可以用于获取基金的日线数据，此方法与fetch_daily_data功能有部分重合，但是此方法会自动更新数据库缺失数据，这是一个更通用的方法，用于
                不关注数据是否存在数据库中的情况
        方法实现：查询数据库中的日线数据，如果日线数据为空或者缺失数据，则调用fetch_daily_data方法获取数据，然后更新数据库，否则直接返回数据库中的数据
        Args:
            asset_id (int): 可选，资产ID,与asset_code不能同时为空，此参数不会改变data_box初始化时设置的asset_id
            asset_code (AssetCode): 可选资产代码，与asset_id不能同时为空
            start_date (datetime): 可选，开始日期，如果为空，默认为当天或最近的一个交易日
            end_date (datetime): 可选，结束日期，如果为空，默认为当天或最近的一个交易日

        Returns:

        """
        if asset_id is None and asset_code is None:
            raise ValueError('asset_id and asset_code can not be None at the same time')
        # 如果asset_id不为空，查询asset_code
        if asset_id is not None:
            asset_code = AssetCode.query.filter(AssetCode.asset_id == asset_id).first()
        # 如果start_date和end_date都为空，则默认使用当天的日期
        if start_date is None and end_date is None:
            # 如果当前时间小于九点三十分，使用昨天日期作为start_date和end_date
            now = datetime.now()
            # 判断今天是否为交易日
            if web_utils.is_trading_day(now):
                # 获取今天的九点三十分
                target = datetime(now.year, now.month, now.day, 9, 30)
                start_date = end_date = (now - timedelta(days=1)).date() if now < target else now.date()
            else:
                # 如果不是交易日，使用最近的一个交易日
                start_date = end_date = web_utils.get_last_trading_day(now)
        else:
            # 使用web_utils转换date
            start_date = web_utils.to_date(start_date)
            end_date = web_utils.to_date(end_date)
        # 查询数据库中是否有数据
        daily_data: List[AssetFundDailyData] = db.session.query(AssetFundDailyData).filter(
            AssetFundDailyData.asset_id == asset_code.asset_id,
            AssetFundDailyData.f_date >= start_date,
            AssetFundDailyData.f_date <= end_date) \
            .order_by(AssetFundDailyData.f_date.asc()).all()
        # 判断日线数据中是否有缺失数据
        if len(daily_data) == 0:
            daily_data = self.fetch_daily_data(asset_code=asset_code, start_date=start_date, end_date=end_date)
            db.session.add_all(daily_data)
            db.session.commit()
            return daily_data
        # 获取最近的日期
        last_date: datetime = daily_data[-1].f_date
        # 如果最近的日期小于end_date，则需要更新数据库中的数据
        if last_date.date() < end_date:
            daily_data.extend(self.fetch_daily_data(asset_code=asset_code, start_date=last_date, end_date=end_date))
            # db.session.add_all(daily_data)
            db.session.bulk_save_objects(daily_data, return_defaults=True, update_changed=True)
            db.session.commit()
        return daily_data
    
    def get_dividend_yield(
        self,
        symbol: str,
        asset_type: AssetTypeEnum = AssetTypeEnum.INDEX,
        source: Optional[str | DataBoxAdapterEnum] = None,
        market: Optional[MarketEnum] = None,
    ) -> Optional[IndexDividendYieldData]:
        """
        获取证券指数的股息率数据
        
        Args:
            symbol: 证券代码
            asset_type: 资产类型，默认为指数类型
            source: 首选数据来源，若为None则自动选择
            market: 市场，可选参数，用于适配器选择
            
        Returns:
            IndexDividendYieldData: 股息率数据，失败返回None
        """
        # 优先尝试通过适配器服务获取（若提供 market 可参与选择）
        adapter = self.adapter_service.get_indicator_adapter(
            indicator=IndicatorEnum.DIVIDEND_YIELD,
            symbol=symbol,
            asset_type=asset_type,
            market=market,
            preferred=source,
        )

        # 无论是否获取到adapter，均交由服务层统一执行；
        # 若指定了 source 且不具备能力，服务层会抛出异常（严格模式）。
        return self.index_valuation_service.get_dividend_yield(
            symbol=symbol,
            asset_type=asset_type,
            source=source if source is not None else DataBoxAdapterEnum.AKSHARE,
            valuation_provider=adapter,
        )
    



dataBox = DataBox
dbox = DataBox
