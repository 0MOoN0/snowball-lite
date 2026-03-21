"""
定义一个类TorxiongAdapter，继承自DataBoxDataAdapter，fetch_all_stock_asset，该方法返回一个AssetStockDTO列表
"""
from typing import List

import requests

from web.common.enum.TorxiongAdapterEnum import TorxiongAdapterEnum
from web.common.utils.WebUtils import web_utils
from web.databox.adapter.data import DataBoxDataAdapter
from web.models.asset.asset import AssetStockDTO, AssetCurrentDTO
from decimal import Decimal


class TorxiongAdapter(DataBoxDataAdapter):
    def fetch_all_stock_asset(self) -> List[AssetStockDTO]:
        """
        方法内容：初始化所有股票资产数据，目前只支持A股股票数据 \n
        数据来源说明：doctorxiong.club（免费接口限制每小时一百次，数据接口相对来说没有那么清晰，没有分ETF 和股票等内容） \n
        设计目的：在更新持仓数据时，需要知道对应仓位的代码和名称，由于持仓数据格式的原因，无法通过get_rt获取，其他接口可以获取持仓数据，但有次数限制 \n
            因此设计一个接口，用于获取所有股票的代码和名称，以便在更新持仓数据时使用可以用到
        方法实现： \n
            使用request发送一个https请求到url：https://api.doctorxiong.club/v1/stock/all，将返回JSON数据，如果code不为200，输入异常日志并抛出异常
            如果code为200，取出data字段，data字段为一个列表，每个元素为一个列表，列表的第一个元素为股票代码(code)，第二个元素为股票名称(stock_name)
            转换成AssetStockDTO列表后返回
        Returns:
            List[AssetStockDTO] : 返回一个AssetStockDTO列表
        """
        response = requests.get('https://api.doctorxiong.club/v1/stock/all')
        if response.status_code != 200 and response.json(['code']) != 200:
            raise RuntimeError('fetch stock asset data failed, status code : %d' % response.status_code)
        data = response.json()['data']
        result = []
        for item in data:
            # 判断stock_name是否为A股
            if not web_utils.is_A_sahres(item[1]):
                continue
            result.append(AssetStockDTO(code=item[0].upper(), stock_name=item[1]))
        return result

    def get_rt(self, code) -> AssetCurrentDTO:
        """
        方法内容：根据代码，获取实时数据和内容 \n
            注：目前只处理股票数据，如果返回的数据没有股票，则会抛出异常
        方法目的：用于某些情况下无法根据代码获取数据时，请求网络接口，获取数据 \n
        方法实现：调用获取股票基础信息接口:https://api.doctorxiong.club/v1/stock ,请求参数为code，对应入参 \n
                将返回JSON数据，如果code不为200，输入异常日志并抛出异常 \n
                取出data字段，data的第一个元素为数据，类型为字典，字段的code大写后为资产代码，name为资产名称（带交易所编号，如：SZ000001），price为字符串，需要转换成数字并乘以1000倍 \n
                最终将结果转换成AssetCurrentDTO对象返回 \n
        Returns:
            AssetCurrentDTO : 返回一个AssetCurrentDTO对象
        """
        response = requests.get('https://api.doctorxiong.club/v1/stock', params={'code': code})
        if response.status_code != 200 and response.json(['code']) != 200:
            raise RuntimeError('fetch stock asset data failed, status code : %d' % response.status_code)
        # 遍历data，如果type为股票，则取出该数据，否则继续遍历
        data = None
        for item in response.json()['data']:
            # 解析data的type数据
            asset_type = item.get('type', None)
            if (asset_type == TorxiongAdapterEnum.STOCK or asset_type == TorxiongAdapterEnum.STOCK_A or
                    asset_type == TorxiongAdapterEnum.STOCK_B or asset_type == TorxiongAdapterEnum.STOCK_A_KCB or
                    asset_type == TorxiongAdapterEnum.STOCK_A_ZXB or asset_type == TorxiongAdapterEnum.STOCK_A_YCB):
                data = item
                break
        if data is None:
            raise RuntimeError(
                'fetch stock asset data failed, stock not found, stock code is %s and the response data is %s'
                % (code, response.json()['data']))
        return AssetCurrentDTO(code=data['code'].upper(), name=data['name'], price=int(Decimal(data['price']) * 1000))
