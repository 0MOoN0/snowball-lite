from _decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple

import pandas as pd
from flask_restful import Resource, Api, reqparse
from pandas import DataFrame

from web.common.cons import webcons
from web.common.enum.routers.charts.daily_type_enum import DailyTypeEnum
from web.common.utils import R
from web.models import db
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.asset.asset import Asset
from web.models.asset.AssetFundDailyData import AssetFundDailyData, AssetFundDailyDataChartsSchema
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.record.record import Record, RecordSchema
from web.routers.charts import charts_bp
from web.services.asset.asset_service import asset_service
from web.weblogger import debug

grid_record_charts_api = Api(charts_bp)

# 常量定义，避免魔法值
class RecordMarkerKeys:
    """交易记录标记点的键名常量，用于统一管理交易记录标记点数据框中的列名"""
    DATE = 'date'      # 交易日期
    DIRECTION = 'direction'  # 交易方向（买入/卖出）
    PRICE = 'price'    # 交易价格
    VALUE = 'value'    # 交易时的净值


class GridRecordChartsRouters(Resource):
    """
    网格交易记录图表数据接口
    
    提供网格交易相关的图表数据，包括日线数据、净值数据、移动均线、交易记录标记点等
    """

    def get(self, grid_type_id: int):
        """
        @@@
        # 功能说明
        获取网格交易记录图表数据，包括K线图数据、净值数据、移动均线、交易记录标记点等
        
        # 接口说明
        接口链接：`/charts/grid_record/{grid_type_id}`

        请求方式：`GET`

        路径参数：
        ```
            grid_type_id: 网格类型ID，必填，整数类型
        ```

        查询参数：
        ```
            data_type：数据类型，可选，默认值为'daily'
                daily：日线数据（包含开盘价、收盘价、最高价、最低价等K线数据）
                netvalue：净值数据（净值相关数据）
                
            daily_type：日线数据类型，可选，默认值为'close'
                close：收盘价
                netvalue：净值
                totvalue：总值
        ```
        
        # 返回数据说明
        返回格式：JSON
        
        成功返回：
        ```json
        {
            "code": 200,
            "msg": "success",
            "data": {
                "xAxis": ["2023-01-01", "2023-01-02", ...],  // 日期数组
                "series": [
                    {
                        "data": {
                            "f_open": ["10.25", "10.30", ...],  // 开盘价
                            "f_close": ["10.28", "10.35", ...],  // 收盘价
                            "f_low": ["10.20", "10.25", ...],  // 最低价
                            "f_high": ["10.35", "10.40", ...]  // 最高价
                        },
                        "markPoint": [  // 交易记录标记点
                            {"date": "2023-01-05", "direction": "买入", "price": "10.25"},
                            {"date": "2023-01-10", "direction": "卖出", "price": "10.50"}
                        ],
                        "markLines": ["9.50", "10.00", "10.50"]  // 网格买卖点位
                    },
                    {"MA20": ["10.30", "10.32", ...]},  // 20日移动均线
                    {"MA51": ["10.25", "10.28", ...]},  // 51日移动均线
                    {"MA120": ["10.20", "10.22", ...]},  // 120日移动均线
                    {"MA250": ["10.15", "10.18", ...]},  // 250日移动均线
                    {"unitCost": ["10.10", "10.12", ...]},  // 单位成本
                    {"f_volume": ["12345", "23456", ...]}  // 成交量
                ]
            }
        }
        ```
        
        失败返回：
        ```json
        {
            "code": 500,
            "msg": "资产数据不存在"
        }
        ```
        
        # 示例
        请求示例：
        ```
        GET /charts/grid_record/123
        GET /charts/grid_record/123?data_type=netvalue&daily_type=totvalue
        ```
        @@@
        """
        # 解析请求参数
        parser = reqparse.RequestParser()
        parser.add_argument('data_type', type=str, required=False, default='daily',
                            help='数据类型 (daily/netvalue)', location='args')
        parser.add_argument('daily_type', type=str, required=False, default='close',
                            help='日线数据类型 (close/netvalue/totvalue)', location='args')
        args = parser.parse_args()
        
        data_type = args.get('data_type', 'daily').lower()
        daily_type = args.get('daily_type', 'close').lower()
        
        # 打印debug日志，参数类型
        debug(f'进入网格交易记录图表数据获取方法，参数grid_type_id：{grid_type_id}，data_type：{data_type}，daily_type：{daily_type}')
        
        # 根据网格类型ID获取资产数据
        asset: Asset = asset_service.get_asset_by_grid_id(grid_type_id)
        # 如果资产数据不存在，抛出异常
        if asset is None:
            return R.fail("资产数据不存在")
            
        # 获取原始数据
        daily_datas, charts_schema = self._get_raw_data(asset.id)
        
        # 根据数据类型处理不同的数据
        if data_type == 'daily':
            return self._process_daily_data(daily_datas, charts_schema, grid_type_id, asset)
        elif data_type == 'netvalue':
            return self._process_netvalue_data(daily_datas, charts_schema, grid_type_id, asset, daily_type)
        else:
            return R.fail(f"不支持的数据类型: {data_type}")

    def _get_raw_data(self, asset_id: int) -> Tuple[List[AssetFundDailyData], AssetFundDailyDataChartsSchema]:
        """
        获取资产的原始日线数据
        
        Args:
            asset_id: 资产ID
            
        Returns:
            Tuple[List[AssetFundDailyData], AssetFundDailyDataChartsSchema]: 
                - 日线数据列表
                - 图表数据模式对象
        """
        # 获取日线数据
        daily_datas: List[AssetFundDailyData] = AssetFundDailyData.query \
            .filter(AssetFundDailyData.asset_id == asset_id) \
            .order_by(AssetFundDailyData.f_date.asc()).all()
        charts_schema = AssetFundDailyDataChartsSchema()
        return daily_datas, charts_schema
        
    def _process_daily_data(self, daily_datas: List[AssetFundDailyData], 
                           charts_schema: AssetFundDailyDataChartsSchema,
                           grid_type_id: int, asset: Asset) -> Dict:
        """
        处理日线数据，返回包含开盘价、收盘价等K线信息的数据
        
        处理流程:
        1. 转换为DataFrame进行数据处理
        2. 清洗和格式化数据
        3. 获取交易记录标记点
        4. 添加单位成本数据
        5. 计算移动均线
        6. 获取网格买卖点位
        7. 构建返回数据结构
        
        Args:
            daily_datas: 日线数据列表
            charts_schema: 图表数据模式对象
            grid_type_id: 网格类型ID
            asset: 资产对象
            
        Returns:
            Dict: 包含K线图数据、移动均线、交易记录标记点等的图表数据
        """
        # 转换为DataFrame进行处理
        daily_df: DataFrame = DataFrame(charts_schema.dump(daily_datas, many=True))[
            [charts_schema.DATE, charts_schema.OPEN,
             charts_schema.CLOSE, charts_schema.HIGH, charts_schema.LOW,charts_schema.VOLUME]]
             
        # 数据列
        data_keys = [charts_schema.OPEN,
                    charts_schema.CLOSE, charts_schema.HIGH, charts_schema.LOW,
                    charts_schema.VOLUME]
                    
        # 数据清洗与格式转换
        daily_df = self._clean_and_format_dataframe(daily_df, charts_schema, data_keys)
        
        # 获取交易记录标记点 - 直接使用交易记录的价格
        record_df = self._get_daily_record_markers(grid_type_id, daily_df, charts_schema)
        
        # 获取单位成本数据
        daily_df = self._add_unit_cost_data(daily_df, asset, charts_schema)
        
        # 计算移动均线 (基于收盘价)
        daily_df = self._calculate_moving_averages(daily_df, charts_schema.CLOSE)
        
        # 获取网格买卖点位
        mark_lines = self._get_grid_mark_lines(grid_type_id)
        
        # 构建返回数据
        x_axis = daily_df[charts_schema.DATE].tolist()
        series = [
            {
                'data': {
                    charts_schema.OPEN: daily_df[charts_schema.OPEN].tolist(),
                    charts_schema.CLOSE: daily_df[charts_schema.CLOSE].tolist(),
                    charts_schema.LOW: daily_df[charts_schema.LOW].tolist(),
                    charts_schema.HIGH: daily_df[charts_schema.HIGH].tolist()
                },
                'markPoint': record_df.to_dict(orient='records') if not record_df.empty else [],
                'markLines': mark_lines
            },
            {'MA20': daily_df['MA20'].tolist()},
            {'MA51': daily_df['MA51'].tolist()},
            {'MA120': daily_df['MA120'].tolist()},
            {'MA250': daily_df['MA250'].tolist()},
            {'unitCost': daily_df['unitCost'].tolist() if 'unitCost' in daily_df.columns else []},
            {charts_schema.VOLUME: daily_df[charts_schema.VOLUME].tolist()}
        ]
        
        return R.charts_data(x_axis=x_axis, series=series, mark_point=[])
        
    def _process_netvalue_data(self, daily_datas: List[AssetFundDailyData], 
                              charts_schema: AssetFundDailyDataChartsSchema,
                              grid_type_id: int, asset: Asset,
                              daily_type: str = 'close') -> Dict:
        """
        处理净值数据，返回净值相关的图表数据
        
        处理流程:
        1. 确定要使用的净值列（收盘价/净值/总值）
        2. 转换为DataFrame进行数据处理
        3. 清洗和格式化数据
        4. 获取净值类型的交易记录标记点
        5. 添加单位成本数据
        6. 计算移动均线
        7. 获取网格买卖点位
        8. 构建返回数据结构
        
        Args:
            daily_datas: 日线数据列表
            charts_schema: 图表数据模式对象
            grid_type_id: 网格类型ID
            asset: 资产对象
            daily_type: 日线数据类型，可选值：'close'(收盘价)/'netvalue'(净值)/'totvalue'(总值)
            
        Returns:
            Dict: 包含净值数据、移动均线、交易记录标记点等的图表数据
        """
        # 确定要使用的净值列
        value_column = self._get_daily_type_column(daily_type)
        
        # 转换为DataFrame进行处理
        columns_to_extract = [charts_schema.DATE, value_column]
        if value_column != charts_schema.NET_VALUE:
            columns_to_extract.append(charts_schema.NET_VALUE)  # 如果需要NET_VALUE用于标记点
            
        daily_df: DataFrame = DataFrame(charts_schema.dump(daily_datas, many=True))[columns_to_extract]
        
        # 数据清洗与格式转换
        daily_df = self._clean_and_format_dataframe(daily_df, charts_schema, [col for col in columns_to_extract if col != charts_schema.DATE])
        
        # 获取净值类型的交易记录标记点
        record_df = self._get_netvalue_record_markers(grid_type_id, daily_df, charts_schema, value_column)
        
        # 获取单位成本数据
        daily_df = self._add_unit_cost_data(daily_df, asset, charts_schema)
        
        # 计算移动均线 (基于指定的净值类型)
        daily_df = self._calculate_moving_averages(daily_df, value_column)
        
        # 获取网格买卖点位
        mark_lines = self._get_grid_mark_lines(grid_type_id)
        
        # 构建返回数据
        x_axis = daily_df[charts_schema.DATE].tolist()
        
        # 构建series数据
        series = [
            {
                'data': {
                    value_column: daily_df[value_column].tolist()
                },
                'markPoint': record_df.to_dict(orient='records') if not record_df.empty else [],
                'markLines': mark_lines
            },
            {'MA20': daily_df['MA20'].tolist()},
            {'MA51': daily_df['MA51'].tolist()},
            {'MA120': daily_df['MA120'].tolist()},
            {'MA250': daily_df['MA250'].tolist()},
            {'unitCost': daily_df['unitCost'].tolist() if 'unitCost' in daily_df.columns else []}
        ]
        
        return R.charts_data(x_axis=x_axis, series=series, mark_point=[])
    
    def _clean_and_format_dataframe(self, df: DataFrame, charts_schema: AssetFundDailyDataChartsSchema, 
                                    data_keys: List[str]) -> DataFrame:
        """
        清洗和格式化数据框
        
        处理内容:
        1. 删除包含空值的行
        2. 日期格式化为YYYY-MM-DD格式
        3. 数值格式化（除以10000并转换为字符串）
        
        Args:
            df: 待处理的数据框
            charts_schema: 图表数据模式对象
            data_keys: 需要处理的数据列名列表
            
        Returns:
            DataFrame: 清洗和格式化后的数据框
        """
        # 删除包含空值的行
        df.dropna(axis=0, how='any', inplace=True)
        
        # 日期格式化
        df[charts_schema.DATE] = pd.to_datetime(df[charts_schema.DATE]).dt.date
        
        # 数值格式化（除以10000并转换为字符串）
        df[data_keys] = df[data_keys].applymap(lambda x: str(Decimal(x) / 10000) if x is not None else None)
        
        # 日期转为字符串格式
        df[charts_schema.DATE] = df[charts_schema.DATE].apply(lambda x: x.strftime('%Y-%m-%d'))
        
        return df
    
    def _get_daily_record_markers(self, grid_type_id: int, daily_df: DataFrame, 
                           charts_schema: AssetFundDailyDataChartsSchema) -> DataFrame:
        """
        获取日线数据的交易记录标记点（使用交易价格）
        
        根据网格类型ID查询相关交易记录，并将交易价格作为标记点，用于在K线图上显示买卖点
        
        处理流程:
        1. 查询网格类型的交易记录
        2. 转换为DataFrame并选择需要的列
        3. 格式化日期和价格
        4. 合并交易记录和日线数据的日期
        5. 去除空值
        
        Args:
            grid_type_id: 网格类型ID
            daily_df: 日线数据框
            charts_schema: 图表数据模式对象
            
        Returns:
            DataFrame: 包含日期、交易方向和价格的交易记录标记点数据框
        """
        # 查询网格类型的交易记录
        records = Record.query.join(GridTypeRecord, Record.id == GridTypeRecord.record_id) \
            .filter(GridTypeRecord.grid_type_id == grid_type_id).all()
            
        record_df = DataFrame()
        if records:
            record_schema = RecordSchema()
            record_df: DataFrame = DataFrame(record_schema.dump(records, many=True))
            if not record_df.empty:
                # 选择需要的列并重命名
                record_df = record_df[[
                    Record.transactions_date.key, 
                    Record.transactions_direction.key,
                    Record.transactions_price.key
                ]]
                
                record_df.rename(columns={
                    Record.transactions_date.key: RecordMarkerKeys.DATE,
                    Record.transactions_direction.key: RecordMarkerKeys.DIRECTION,
                    Record.transactions_price.key: RecordMarkerKeys.PRICE
                }, inplace=True)
                
                # 日期格式化
                record_df[RecordMarkerKeys.DATE] = pd.to_datetime(record_df[RecordMarkerKeys.DATE]).dt.date
                record_df[RecordMarkerKeys.DATE] = record_df[RecordMarkerKeys.DATE].apply(lambda x: x.strftime(webcons.DataFormatStr.Y_m_d))
                
                # 价格格式化（除以10000）
                record_df[RecordMarkerKeys.PRICE] = record_df[RecordMarkerKeys.PRICE].apply(lambda x: str(Decimal(x) / 1000))
                
                # 合并交易记录和日线数据的日期
                record_df = pd.merge(
                    daily_df[[charts_schema.DATE]], 
                    record_df, 
                    how='inner', 
                    left_on=charts_schema.DATE, 
                    right_on=RecordMarkerKeys.DATE
                )
                
                # 去除空值
                record_df.dropna(axis=0, how='any', inplace=True)
        
        return record_df
    
    def _get_netvalue_record_markers(self, grid_type_id: int, daily_df: DataFrame, 
                                    charts_schema: AssetFundDailyDataChartsSchema,
                                    value_column: str) -> DataFrame:
        """
        获取净值数据的交易记录标记点（使用净值）
        
        根据网格类型ID查询相关交易记录，并将对应日期的净值作为标记点，用于在净值图上显示买卖点
        
        处理流程:
        1. 查询网格类型的交易记录
        2. 转换为DataFrame并选择需要的列
        3. 格式化日期
        4. 合并交易记录和日线数据，获取对应日期的净值
        5. 创建新的标记点DataFrame
        6. 去除空值
        
        Args:
            grid_type_id: 网格类型ID
            daily_df: 日线数据框
            charts_schema: 图表数据模式对象
            value_column: 值列名（收盘价/净值/总值）
            
        Returns:
            DataFrame: 包含日期、交易方向和净值的交易记录标记点数据框
        """
        # 查询网格类型的交易记录
        records = Record.query.join(GridTypeRecord, Record.id == GridTypeRecord.record_id) \
            .filter(GridTypeRecord.grid_type_id == grid_type_id).all()
            
        record_df = DataFrame()
        if records:
            record_schema = RecordSchema()
            record_df: DataFrame = DataFrame(record_schema.dump(records, many=True))
            if not record_df.empty:
                # 选择需要的列并重命名
                record_df = record_df[[
                    Record.transactions_date.key, 
                    Record.transactions_direction.key
                ]]
                
                record_df.rename(columns={
                    Record.transactions_date.key: RecordMarkerKeys.DATE,
                    Record.transactions_direction.key: RecordMarkerKeys.DIRECTION
                }, inplace=True)
                
                # 日期格式化
                record_df[RecordMarkerKeys.DATE] = pd.to_datetime(record_df[RecordMarkerKeys.DATE]).dt.date
                record_df[RecordMarkerKeys.DATE] = record_df[RecordMarkerKeys.DATE].apply(lambda x: x.strftime(webcons.DataFormatStr.Y_m_d))
                
                # 合并交易记录和日线数据，获取净值
                merged_df = pd.merge(
                    daily_df[[charts_schema.DATE, value_column]], 
                    record_df, 
                    how='inner', 
                    left_on=charts_schema.DATE, 
                    right_on=RecordMarkerKeys.DATE
                )
                
                # 确保合并后的数据有所需的值
                if not merged_df.empty:
                    # 创建新的标记点DataFrame，使用净值
                    record_df = merged_df[[charts_schema.DATE, value_column, RecordMarkerKeys.DIRECTION]]
                    record_df.rename(columns={value_column: RecordMarkerKeys.VALUE}, inplace=True)
                    
                    # 去除空值
                    record_df.dropna(axis=0, how='any', inplace=True)
                else:
                    record_df = DataFrame()
        
        return record_df
    
    def _add_unit_cost_data(self, daily_df: DataFrame, asset: Asset, 
                           charts_schema: AssetFundDailyDataChartsSchema) -> DataFrame:
        """
        添加单位成本数据
        
        查询资产的单位成本数据，并添加到日线数据中，用于在图表上显示成本线
        
        处理流程:
        1. 查询资产的单位成本数据
        2. 转换为DataFrame并格式化
        3. 合并到日线数据中
        4. 填充缺失值，使图形更加连续美观
        
        Args:
            daily_df: 日线数据框
            asset: 资产对象
            charts_schema: 图表数据模式对象
            
        Returns:
            DataFrame: 添加了单位成本列的数据框
        """
        # 查询单位成本
        trade_datas = db.session.query(TradeAnalysisData.record_date, TradeAnalysisData.unit_cost).filter(
            TradeAnalysisData.asset_id == asset.id,
            TradeAnalysisData.analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value) \
            .all()
            
        if trade_datas:
            trade_df: DataFrame = DataFrame(trade_datas, columns=[TradeAnalysisData.record_date.key,
                                                                  TradeAnalysisData.unit_cost.key])
            # 重命名列
            trade_df.rename(columns={TradeAnalysisData.record_date.key: RecordMarkerKeys.DATE,
                                     TradeAnalysisData.unit_cost.key: 'unitCost'}, inplace=True)
            trade_df['unitCost'] = trade_df['unitCost'].apply(lambda x: str(Decimal(x) / 10000))
            
            # 转换日期格式并合并
            trade_df[RecordMarkerKeys.DATE] = pd.to_datetime(trade_df[RecordMarkerKeys.DATE]).dt.date
            trade_df[RecordMarkerKeys.DATE] = trade_df[RecordMarkerKeys.DATE].apply(lambda x: x.strftime(webcons.DataFormatStr.Y_m_d))
            daily_df = pd.merge(daily_df, trade_df, how='left', left_on=charts_schema.DATE, right_on=RecordMarkerKeys.DATE)
            
            # 填充unitCost，使图形更加美观
            daily_df['unitCost'] = daily_df['unitCost'].ffill()
            
            # 替换nan为None
            daily_df['unitCost'] = daily_df['unitCost'].astype(str)
        else:
            # 如果没有单位成本数据，添加空的unitCost列
            daily_df['unitCost'] = ''
            
        return daily_df
    
    def _calculate_moving_averages(self, daily_df: DataFrame, base_column: str) -> DataFrame:
        """
        计算移动均线
        
        根据基准列计算多个周期的移动均线（MA20、MA51、MA120、MA250）
        
        处理流程:
        1. 将基准列转换为数值类型
        2. 计算各个周期的移动均线
        3. 格式化移动均线数据
        4. 删除临时列
        
        Args:
            daily_df: 日线数据框
            base_column: 基准列名（用于计算移动均线的列，如收盘价、净值等）
            
        Returns:
            DataFrame: 添加了移动均线列的数据框
        """
        # 仅当数据充足时计算移动均线
        if len(daily_df) > 0 and base_column in daily_df.columns:
            # 转换为数值类型进行计算
            daily_df[base_column + '_numeric'] = daily_df[base_column].apply(
                lambda x: float(x) if x and x != 'None' else None)
                
            # 计算各个周期的移动均线
            for period in [20, 51, 120, 250]:
                ma_column = f'MA{period}'
                if len(daily_df) >= period:
                    daily_df[ma_column] = daily_df[base_column + '_numeric'].rolling(window=period).mean().round(4).astype(str)
                else:
                    daily_df[ma_column] = ''
                    
            # 删除临时列
            daily_df.drop(columns=[base_column + '_numeric'], inplace=True, errors='ignore')
        else:
            # 添加空的移动均线列
            for period in [20, 51, 120, 250]:
                daily_df[f'MA{period}'] = ''
                
        return daily_df
    
    def _get_grid_mark_lines(self, grid_type_id: int) -> List[str]:
        """
        获取网格买卖点位
        
        查询网格类型详情，提取买入价格作为标记线，用于在图表上显示网格线
        
        Args:
            grid_type_id: 网格类型ID
            
        Returns:
            List[str]: 网格买入价格列表（字符串格式）
        """
        # 查询网格类型详情
        detail_list: list[GridTypeDetail] = GridTypeDetail.query. \
            filter(GridTypeDetail.grid_type_id == grid_type_id).all()
            
        # 提取买入价格作为标记线
        mark_lines = [str(Decimal(detail.trigger_purchase_price) / 10000) for detail in detail_list]
        
        return mark_lines
    
    def _get_daily_type_column(self, daily_type: str) -> str:
        """
        获取对应的数据列名
        
        根据日线数据类型参数返回对应的数据列名
        
        Args:
            daily_type: 日线数据类型，可选值：'close'(收盘价)/'netvalue'(净值)/'totvalue'(总值)
            
        Returns:
            str: 对应的数据列名
        """
        # 默认使用收盘价
        if daily_type is None:
            return AssetFundDailyData.f_close.key
            
        # 转为大写以匹配枚举
        daily_type = daily_type.upper()
        
        if daily_type == 'NETVALUE' or daily_type == DailyTypeEnum.NETVALUE.name:
            return AssetFundDailyData.f_netvalue.key
        elif daily_type == 'TOTVALUE' or daily_type == DailyTypeEnum.TOTVALUE.name:
            return AssetFundDailyData.f_totvalue.key
        else:  # 默认返回收盘价
            return AssetFundDailyData.f_close.key


def _get_daily_type(daily_type: str):
    """
    获取日线数据类型对应的列名（旧版方法，建议使用 _get_daily_type_column）
    
    Args:
        daily_type: 日线数据类型，可选值：'close'(收盘价)/'netvalue'(净值)/'totvalue'(总值)
        
    Returns:
        str: 对应的数据列名
    """
    # 将type转为大写
    if daily_type is None or not hasattr(DailyTypeEnum, daily_type.upper()):
        return AssetFundDailyData.f_close.key
    daily_type: str = daily_type.upper()
    if DailyTypeEnum[daily_type] == DailyTypeEnum.NETVALUE:
        return AssetFundDailyData.f_netvalue.key
    elif DailyTypeEnum[daily_type] == DailyTypeEnum.TOTVALUE:
        return AssetFundDailyData.f_totvalue.key
    return AssetFundDailyData.f_close.key


grid_record_charts_api.add_resource(GridRecordChartsRouters, '/grid_record/<int:grid_type_id>')
