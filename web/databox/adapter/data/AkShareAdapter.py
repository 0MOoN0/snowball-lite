from datetime import datetime, date
from typing import Optional, List

import pandas as pd

from web.weblogger import logger

mod_logger = logger.getChild(__name__)

try:
    import akshare as ak
except ImportError:
    ak = None
    logger.warning("AkShare library not available")

from web.databox.interfaces import SecurityIndexValuationInterface
from web.databox.interfaces.convertible_bond_interface import ConvertibleBondIssuanceInterface
from web.databox.models.dividend_yield import IndexDividendYieldData
from web.common.enum.asset_enum import AssetTypeEnum
from web.common.enum.common_enum import CurrencyEnum, MarketEnum
from web.databox.enum.DataSourceEnum import DataSourceEnum
from web.databox.models.dto.convertible_bond_issuance import ConvertibleBondIssuanceData
from web.databox.schemas.convertible_bond_issuance_schema import ConvertibleBondIssuanceSchema


class AkShareAdapter(SecurityIndexValuationInterface, ConvertibleBondIssuanceInterface):
    """
    AkShare数据适配器
    实现 SecurityIndexValuationInterface 接口，提供指数股息率等指标数据
    
    特性：
    - 仅支持指数（INDEX）资产类型的股息率查询；
    - 基于 akshare.stock_zh_index_value_csindex 接口获取中证指数估值数据；
    - 自动从最新一行数据解析股息率字段（优先使用“股息率2”）；
    - 返回值单位为百分比。
    
    异常与容错：
    - 当 akshare 未安装或调用失败时，记录日志并抛出 ImportError/返回 None；
    - 当未获取到有效数据或字段缺失时，返回 None。
    """
    
    def __init__(self):
        super().__init__()
        if ak is None:
            mod_logger.error("AkShare library is not available")
            raise ImportError("AkShare library is required but not installed")
    
    def get_dividend_yield(self, symbol: str, asset_type: AssetTypeEnum = AssetTypeEnum.INDEX) -> Optional[IndexDividendYieldData]:
        """
        获取指数股息率数据（AkShare实现）
        
        参数：
        - symbol: 指数代码
        - asset_type: 资产类型，仅支持指数（INDEX）
        
        返回：
        - IndexDividendYieldData | None: 成功返回数据对象，失败返回 None
        
        实现细节：
        - 调用 ak.stock_zh_index_value_csindex(symbol) 获取估值数据
        - 取最新一行，优先读取字段“股息率2”作为股息率
        - 无数据或字段为空时返回 None
        """
        try:
            if asset_type == AssetTypeEnum.INDEX:
                # 使用中证指数估值接口获取指数股息率数据
                try:
                    index_value_data = ak.stock_zh_index_value_csindex(symbol=symbol)
                    
                    if index_value_data.empty:
                        mod_logger.warning(f"Index value data for {symbol} not found")
                        return None
                    
                    # 获取最新的估值数据
                    latest_data = index_value_data.iloc[-1]
                    
                    # 提取股息率数据（根据文档，字段名可能是'股息率1'或'股息率2'）
                    dividend_yield = None
                    if '股息率2' in latest_data and pd.notna(latest_data['股息率2']):
                        dividend_yield = float(latest_data['股息率2'])
                    
                    if dividend_yield is None:
                        mod_logger.warning(f"No dividend yield data found for index {symbol}")
                        return None
                    
                    # 获取指数名称
                    index_name = latest_data.get('指数中文简称', latest_data.get('指数中文全称', f"指数{symbol}"))
                    
                    return IndexDividendYieldData(
                        symbol=symbol,
                        name=index_name,
                        dividend_yield=dividend_yield,
                        currency=CurrencyEnum.CNY.name,
                        update_time=datetime.now(),
                        data_source=DataSourceEnum.AKSHARE_CSINDEX.value
                    )
                    
                except Exception as e:
                    mod_logger.error(f"Error fetching index value data for {symbol}: {str(e)}", exc_info=True)
                    return None
            
        except Exception as e:
            mod_logger.error(f"Error fetching dividend yield for {symbol}: {str(e)}", exc_info=True)
            return None

    # -------------------- 可转债发行（cninfo） --------------------
    def _to_yyyymmdd(self, d: Optional[date | str]) -> Optional[str]:
        """将 date/字符串转换为 akshare 需要的 YYYYMMDD 字符串。"""
        if d is None:
            return None
        try:
            if isinstance(d, str):
                # 如果已经是纯数字 YYYYMMDD，直接返回；否则尝试解析
                if d.isdigit() and len(d) == 8:
                    return d
                dt = pd.to_datetime(d)
            else:
                dt = pd.to_datetime(d)
            return dt.strftime("%Y%m%d")
        except Exception:
            return None

    def get_cb_issuance_cninfo(self, start_date: Optional[date | str], end_date: Optional[date | str]):
        """
        使用 AkShare 的 bond_cov_issue_cninfo 获取可转债发行情况（巨潮资讯）。

        Args:
            start_date: 起始日期，可为 date 或字符串；最终转换为 YYYYMMDD
            end_date: 截止日期，可为 date 或字符串；最终转换为 YYYYMMDD

        Returns:
            pandas.DataFrame: 原始发行数据表；失败时返回空 DataFrame
        """
        if ak is None:
            raise ImportError("AkShare library is required but not installed")
        try:
            sd = self._to_yyyymmdd(start_date)
            ed = self._to_yyyymmdd(end_date)
            if not sd or not ed:
                raise ValueError("start_date/end_date 无法解析为 YYYYMMDD 格式")
            df = ak.bond_cov_issue_cninfo(start_date=sd, end_date=ed)
            if df is None:
                return pd.DataFrame()
            return df
        except Exception as e:
            mod_logger.error(f"Error calling bond_cov_issue_cninfo: {e}", exc_info=True)
            return pd.DataFrame()

    def _normalize_market(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        v = str(value).upper()
        if v.startswith("SH"):
            return "SSE"
        if v.startswith("SZ"):
            return "SZSE"
        # 对于非交易所前缀数据，返回原值或 None
        return None

    def _parse_date(self, value) -> Optional[date]:
        try:
            if pd.isna(value):
                return None
            return pd.to_datetime(value).date()
        except Exception:
            return None

    def _to_dto(self, row: pd.Series) -> ConvertibleBondIssuanceData:
        # 使用 Schema 做字段映射与类型转换（兼容 公告日期/发行日期 字段名差异）
        schema = ConvertibleBondIssuanceSchema()
        data_dict = row.to_dict()
        try:
            # 由 Schema 完成 DTO 构造与日期转换，并注入数据来源
            schema.context = {"data_source": DataSourceEnum.AKSHARE.value}
            dto: ConvertibleBondIssuanceData = schema.load(data_dict)  # type: ignore[assignment]
            return dto
        except Exception as e:
            mod_logger.error(f"Error loading row into schema: {e}", exc_info=True)
            # 最小容错：仅保留核心字段，避免因列差异导致整体失败
            return ConvertibleBondIssuanceData(
                bond_code=str(data_dict.get("债券代码", "")),
                bond_name=str(data_dict.get("债券简称", "")),
                market=data_dict.get("交易市场"),
                full_name=data_dict.get("债券名称"),
                data_source=DataSourceEnum.AKSHARE.value,
                update_time=datetime.now(),
            )

    # 接口实现：返回 DTO 列表
    def list_issuance(self, start_date: date, end_date: date, market: Optional[MarketEnum] = None) -> List[ConvertibleBondIssuanceData]:
        df = self.get_cb_issuance_cninfo(start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            return []
        records: List[ConvertibleBondIssuanceData] = []
        for _, row in df.iterrows():
            dto = self._to_dto(row)
            # 市场过滤：cninfo 为中国市场，若传入 market=CN，则不过滤；其他市场暂不支持
            records.append(dto)
        return records