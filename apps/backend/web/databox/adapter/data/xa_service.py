# -*- coding: UTF-8 -*-
"""
@File    ：xa_service.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/11/10 11:24
"""
import sys
from abc import ABC, abstractmethod
from typing import Dict, List

from flask import has_app_context
from pandas import DataFrame

from web import models
from web.common.cons import webcons
import inspect
import xalpha as xa
from web.databox.models.daily_data import DataBoxDailyData
from web.models.asset.asset import Asset, AssetCurrentDTO


class XaService(ABC):
    def init_adapter(self, xq_token: Dict):
        pass

    @abstractmethod
    def get_rt(self):
        pass

    @abstractmethod
    def fundinfo(self):
        pass

    @abstractmethod
    def get_daily(self, code, *args, **kwargs):
        pass


class XaServiceAdapter(XaService):

    def __init__(self):
        self.fund_info_db_setting = {}
        self.xa = xa

    def init_adapter(self, xq_token: Dict):
        self.xa.universal.set_token(xq_token)
        cache_settings = webcons.apply_xalpha_cache_settings(
            self.xa,
            default_engine=models.db.engine,
        )
        self.fund_info_db_setting = dict(cache_settings["fundinfo"])

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

    def get_daily(self, code, *args, **kwargs) -> DataFrame:
        """
        根据提供的代码获取资产的每日数据列表。

        Args:
            code (str): 资产代码，用于标识要查询的资产。
            *args: 可变位置参数，将传递给 execute_xa 方法。
            **kwargs: 可变关键字参数，将传递给 execute_xa 方法。

        Returns:
            List[DataBoxDailyData]: 包含 DataBoxDailyData 对象的列表，每个对象代表一天的数据。

        Raises:
            不直接抛出异常，但如果在内部处理过程中发生错误，可能通过 execute_xa 方法间接抛出。

        注意:
            - 此方法通过调用 execute_xa 方法获取资产的每日数据，并返回一个包含 DataBoxDailyData 对象的列表。
            - DataBoxDailyData 对象是从每日数据的 DataFrame 中逐行创建的。
        """
        backend_scope = self._daily_backend_scope()
        if backend_scope is None:
            return self.execute_xa(None, code, *args, **kwargs)

        with backend_scope as cache_settings:
            self.fund_info_db_setting = dict(cache_settings["fundinfo"])
            return self.execute_xa(None, code, *args, **kwargs)

    def get_rt(self, code, *args, **kwargs) -> AssetCurrentDTO:
        """
        根据提供的代码获取实时资产信息。

        Args:
            code (str): 资产代码，用于标识要查询的资产。
            *args: 可变位置参数，将传递给 execute_xa 方法。
            **kwargs: 可变关键字参数，将传递给 execute_xa 方法。

        Returns:
            AssetCurrentDTO: 包含资产实时信息的 AssetCurrentDTO 对象。
                如果未找到对应代码的信息，则返回 None。

        Raises:
            不直接抛出异常，但如果在内部处理过程中发生错误，可能通过 execute_xa 方法间接抛出。
        """
        rt = self.execute_xa(None, code, *args, **kwargs)
        if rt is None:
            return None
        market = Asset.get_market_enum()[rt.get('market')].value if rt.get('market') is not None else None
        currency = Asset.get_currency_enum()[rt.get('currency')].value if rt.get('currency') is not None else None
        asset_current_dto = AssetCurrentDTO(name=rt['name'], code=code, price=int(rt['current'] * 1000),
                                            market=market, currency=currency)
        return asset_current_dto

    def fundinfo(self, *args, **kwargs):
        fund_info_kwargs = self._get_fund_info_db_setting()
        fund_info_kwargs.update(kwargs)
        return self.execute_xa(None, *args, **fund_info_kwargs)

    def execute_xa(self, callable_name=None, *args, **kwargs):
        """
        执行 XA 服务中的方法。

        Args:
            callable_name (str, optional): 要执行的方法名。如果未提供，则自动获取调用者的方法名。默认为 None。
            *args: 传递给要执行方法的可变位置参数。
            **kwargs: 传递给要执行方法的可变关键字参数。

        Returns:
            根据执行的方法返回相应的结果。

        Raises:
            AttributeError: 如果指定的方法不存在于 XA 服务中。
        """
        # 获取方法名称，如果callable_name未提供，则使用当前调用者的方法名
        caller_name = callable_name or inspect.currentframe().f_back.f_code.co_name
        try:
            # 获取XA服务中的可执行方法
            executable = getattr(self.xa, caller_name)
            # 执行方法并返回结果
            return executable(*args, **kwargs)
        except AttributeError:
            # 如果方法不存在，则抛出异常
            raise AttributeError(f"The method '{caller_name}' does not exist in XA service.")
