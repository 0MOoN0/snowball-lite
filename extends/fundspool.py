import jqdatasdk as jq
import pandas as pd
from jqdatasdk import finance, query, bond
import xalpha as xa


class FundsPool:
    """
    基金池
    """

    def __init__(self):
        self.bond_fund_pool = None
        self.bond_fund = None
        self.cr_top40 = None
        self.rate_bond_code = None
        self.latest_end_time = None  # 最近更新的end_time
        self.sim_infos = {}  # 基金的信息，包括价格等
        jq.auth("13118859528", "Aa1474838768")

    def get_bond_fund_pool(self, start="2010-01-01", end="2021-01-01"):
        """
        根据时间获取符合条件所有基金
        条件有：1.运行时间超过三年的基金  2.纯债基金  3.运行时间在start和end之间的基金
               4.公司规模排名属于前40
        :param start: str, 开始回测的时间，格式：%Y-%M-%D
        :param end: str, 结束回测的时间，格式：%Y-%M-%D
        :param sim_infos: obj,
        :return: pd.DataFrame, 基金池，按利率债和信用债分组，收益率排序
        """
        if self.bond_fund_pool is not None and self.latest_end_time > start:
            return self.bond_fund_pool
        if self.bond_fund is None:
            bond_fund = pd.read_csv("I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\bond_fund.csv", encoding="gbk",
                                    index_col=0,
                                    header=0)
            self.bond_fund = bond_fund
        if self.cr_top40 is None:
            cr = pd.read_json("I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\company_ranking.json", encoding="utf-8")
            cr_top40 = cr[:40]
            cr_top40.sort_values("assetScale", ascending=False, inplace=True)
            self.cr_top40 = cr_top40
        if self.rate_bond_code is None:
            rate_bond_code = pd.read_csv("I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\rate_bond_code.csv",
                                         encoding="gbk",
                                         index_col=0, header=0)
            self.rate_bond_code = rate_bond_code
        three_start_years_ago = start.replace(start.year - 3)
        # 获取已经运行三年或以上的债券基金
        bond_fund_pool = self.bond_fund[self.bond_fund["start_date"] <= three_start_years_ago].sort_values("end_date")
        # 筛选纯债基金
        # bond_fund_pool = bond_fund_pool[bond_fund_pool.loc[:, "type3"] == "纯债债券型"].copy()
        # 利率债代码
        # 对基金持有债券进行分析
        for fundcode in bond_fund_pool.index:
            # 获取某只债券的持仓，时间在回测开始时间后和回测结束时间前
            bf_bond_holding = finance.run_query(
                query(finance.FUND_PORTFOLIO_BOND).filter(finance.FUND_PORTFOLIO_BOND.code == fundcode[:6],
                                                          finance.FUND_PORTFOLIO_BOND.period_start >= start,
                                                          finance.FUND_PORTFOLIO_BOND.period_end < end))
            bonds_symbol_list = bf_bond_holding["symbol"]  # 获取基金持仓的债券代码列表
            bond_detail = []
            for symbol in bonds_symbol_list:  # 根据债券代码和利率债代码对债券进行分类，分为利率债和信用债
                col = []
                col.append(symbol)
                df = bond.run_query(query(bond.BOND_BASIC_INFO).filter(bond.BOND_BASIC_INFO.code == symbol))
                if df["bond_type_id"].values[0] in self.rate_bond_code.index:
                    col.append("利率债")
                else:
                    col.append("信用债")
                bond_detail.append(col)
            # 将债券基金持仓债券分为利率债和信用债
            bond_detail = pd.DataFrame(bond_detail, columns=["symbol", "bond_type"])
            bf_bond_holding = pd.merge(left=bf_bond_holding, right=bond_detail, how='left', left_on='symbol',
                                       right_on='symbol')
            # 对债券持仓进行分析，计算利率债占比和信用债占比
            sum = bf_bond_holding.groupby('bond_type')['proportion'].sum()
            bond_fund_pool.loc[fundcode, 'type4'] = '信用债' if sum['信用债'] - sum['利率债'] > 0 else '利率债'
            bond_fund_pool.loc[fundcode, 'credit_rate_rate'] = sum['信用债'] / sum['利率债']
            # 获取基金近三年的收益率情况
            if fundcode not in self.sim_infos:
                self.sim_infos[fundcode] = xa.fundinfo("F" + fundcode[:6])
            fund_price = self.sim_infos[fundcode].price[
                (self.sim_infos[fundcode].price['date'] >= three_start_years_ago) & (
                        self.sim_infos[fundcode].price['date'] < start)]
            bond_fund_pool.loc[fundcode + '.OF', 'three_year_yield'] = (fund_price.iloc[-1, -1] -
                                                                        fund_price.iloc[0, -1]) / \
                                                                       fund_price.iloc[0, -1]

        self.latest_end_time = end
        self.bond_fund_pool = bond_fund_pool
        return self.bond_fund_pool
