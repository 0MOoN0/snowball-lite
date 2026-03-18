from xalpha.backtest import Scheduled
from xalpha.backtest import BTE
import pandas as pd
import numpy as np


class ValuationScheduled(Scheduled):
    """
    基于估值择时的无限现金流单只指数定投
    """

    def prepare(self):
        super().prepare()
        self.index_code = self.kws["index_code"]
        self.index_data = pd.read_csv(
            "I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\index_" + self.index_code + "_data.csv",
            index_col=0, header=0)
        self.index_data["date"] = pd.to_datetime(self.index_data["date"])
        self.ref_indicator = self.index_data[["date", "y10_pe_ttm_fs_ewpvo_cvpos"]]
        self.set_fund(self.code, dividend_label=1)

    def run(self, date):
        if date in self.date_range and len(self.ref_indicator[self.ref_indicator["date"] == date]) > 0:
            indicator = self.ref_indicator[self.ref_indicator["date"] == date]["y10_pe_ttm_fs_ewpvo_cvpos"].iloc[0]
            # if 0.10 < indicator <= 0.2:
            #     self.buy(self.code, self.value / 2, date)
            #     self.buy(self.bond_code, self.value / 2, date)
            # elif indicator <= 0.1:
            #     self.buy(self.code, self.value, date)
            # else:
            #     self.buy(self.bond_code, self.value, date)
            if indicator <= 0.3:
                self.buy(self.code, self.value, date)


class ValuationScheduled_SP(BTE):
    def prepare(self):
        self.hs_300_fund = "F000051"
        self.zz_500_fund = "F001052"
        self.hs_300_index = "000300"
        self.zz_500_index = "000905"
        self.hs_300_index_data = pd.read_csv(
            "I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\index_" + self.hs_300_index + "_data.csv",
            index_col=0, header=0)
        self.zz_500_index_data = pd.read_csv(
            "I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\index_" + self.zz_500_index + "_data.csv",
            index_col=0, header=0)
        self.hs_300_index_data["date"] = pd.to_datetime(self.hs_300_index_data["date"])
        self.zz_500_index_data["date"] = pd.to_datetime(self.zz_500_index_data["date"])
        self.zz_500_ref_indicator = self.zz_500_index_data[["date", "y10_pe_ttm_fs_ewpvo_cvpos"]]
        self.hs_300_ref_indicator = self.hs_300_index_data[["date", "y10_pe_ttm_fs_ewpvo_cvpos"]]
        self.set_fund(self.hs_300_fund, dividend_label=1)
        self.set_fund(self.zz_500_fund, dividend_label=1)
        self.value = self.kws["value"]  # 每次投入金额
        self.date_range = self.kws["date_range"]  # pd.data_range 买入日期列表

    def run(self, date):
        if date in self.date_range:
            hs_300_indicator = self.hs_300_ref_indicator[self.hs_300_ref_indicator["date"] == date]
            zz_500_indicator = self.zz_500_ref_indicator[self.zz_500_ref_indicator["date"] == date]
            if len(hs_300_indicator) > 0 and len(zz_500_indicator) > 0:
                hs_300_indicator = hs_300_indicator["y10_pe_ttm_fs_ewpvo_cvpos"].iloc[0]
                zz_500_indicator = zz_500_indicator["y10_pe_ttm_fs_ewpvo_cvpos"].iloc[0]
                if min(hs_300_indicator, zz_500_indicator) < 0.3:
                    if hs_300_indicator < zz_500_indicator:
                        self.buy(code=self.hs_300_fund, value=self.value, date=date)
                    else:
                        self.buy(self.zz_500_fund, self.value, date)


class ValuationScheduled_V2(BTE):
    """
    基于估值的无限现金流多只指数定投
    """

    def prepare(self):
        self.index_fund_dict = self.kws.get("index_fund_dict")  # 格式：index_code:fund_code
        self.index_indicator_dict = self.kws.get("index_indicator_dict")  # 格式：index_code:indicator
        stock_record_name = ["date"]
        self.index_datas = {}  # 指数的数据，格式：index_code:index_data
        self.scheduled = self.kws.get("scheduled", None)  # 是否开启定投
        if self.scheduled is not None:
            self.scheduled_value = self.scheduled.get("scheduled_value")
            self.scheduled_date_range = self.scheduled.get("scheduled_date_range")
        for index_code in self.index_fund_dict:
            fund_code = self.index_fund_dict[index_code]
            self.set_fund(code="F" + fund_code, dividend_label=1)
            # 指数名称
            stock_record_name.append(self.get_info("F" + fund_code).name)
            self.index_datas[index_code] = pd.read_csv(
                "I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\index_" + index_code + "_data.csv",
                index_col=0, header=0)
            self.index_datas[index_code]["date"] = pd.to_datetime(self.index_datas[index_code]["date"])
        self.stock_record = pd.DataFrame(columns=stock_record_name)

    def run(self, date):
        # 判断当前日期是否为操作日
        if date in self.scheduled_date_range:
            # 找出估值为零或者最低的基金
            candicate_list = []
            min_of_fund = 30
            # 遍历指数数据
            buy_fund_code = ""
            hodling_parts = 10000
            for index_code in self.index_datas:
                index_data = self.index_datas[index_code][self.index_datas[index_code]["date"] == date]
                # 如果指数在当前的日期重存在，而且基金也已经成立，则进入下一步判断
                if len(index_data) > 0 and len(self.infos["F" + self.index_fund_dict[index_code]].price[
                                                   self.infos["F" + self.index_fund_dict[index_code]].price[
                                                       "date"] <= date]) > 0:
                    # 如果当前指数估值较小，则选择当前指数
                    indicaort = round(index_data[self.index_indicator_dict[index_code]].iloc[0] * 100, 0)
                    if indicaort < min_of_fund:
                        min_of_fund = round(index_data[self.index_indicator_dict[index_code]].iloc[0] * 100, 0)
                        buy_fund_code = self.index_fund_dict[index_code]
                        hodling_parts = 0 if self.stock_record[
                                                 self.infos["F" + buy_fund_code].name].last_valid_index() is None else \
                            self.stock_record[self.infos["F" + buy_fund_code].name].last_valid_index()
                    # 如果当前指数估值与前面的相等，则判断持仓，如果当前持仓较小，则选择当前指数
                    elif indicaort == min_of_fund and sum(
                            self.stock_record[
                                self.get_info("F" + self.index_fund_dict[index_code]).name]) < hodling_parts:
                        min_of_fund = round(index_data[self.index_indicator_dict[index_code]].iloc[0] * 100, 0)
                        buy_fund_code = self.index_fund_dict[index_code]
                        hodling_parts = 0 if self.stock_record[
                                                 self.infos["F" + buy_fund_code].name].last_valid_index() is None else \
                        self.stock_record[self.infos["F" + buy_fund_code].name].last_valid_index()
            if buy_fund_code != "":
                # 购买基金
                self.buy("F" + buy_fund_code, self.scheduled_value, date)
                # 更新持仓表
                self.stock_record = self.stock_record.append(
                    {"date": date, self.get_info("F" + buy_fund_code).name: hodling_parts + 1},
                    ignore_index=True)


def ValuationScheduled_V2_test():
    data = pd.read_excel("C:\\Users\\Peter\\OneDrive\\文档\\LC\\量化投资\\投资体系品种与仓位.xls", header=0, index_col=0,
                         dtype={"index_code": str, "fund": str})
    index_fund_dict = {}
    index_indicator_dict = {}
    data.dropna(axis=0, how='any', inplace=True, subset=["fund"])
    index_fund_df = data[["index_code", "fund"]]
    index_indicator_df = data[["index_code", "indicator"]]
    for i, row in index_fund_df.iterrows():
        index_fund_dict[row["index_code"]] = row["fund"]
    for i, row in index_indicator_df.iterrows():
        index_indicator_dict[row["index_code"]] = "y10_pe_ttm_fs_ewpvo_cvpos" if row[
                                                                                     "indicator"] == "pe_ttm" else "y10_pb_fs_ew_cvpos"
    scheduled = {"scheduled_value": 5000,
                 "scheduled_date_range": pd.date_range("2009-02-01", "2021-03-01", freq="MS") + pd.DateOffset(days=16)}
    db = ValuationScheduled_V2(start="2009-02-20", end="2021-02-20", totmoney=10000, index_fund_dict=index_fund_dict,
                               index_indicator_dict=index_indicator_dict,
                               verbose=True, scheduled=scheduled)
    db.backtest()
# ValuationScheduled_V2_test()
