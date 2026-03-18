# 回测时的一些脚本
"""
    # 债券基金回测内容

    def prepare(self):
        # 获取十年期国债收益率数据
        self.bond_yield = BondYield().get_bond_yield()
        self.bond_yield["日期"] = pd.to_datetime(self.bond_yield["日期"])  # 字符串转datetime
        # 获取仓位表
        self.positions = Positions(max_positions=100).bond_positions
        self.code = self.kws["code"]
        self.set_fund(code=self.code, dividend_label=1)
        self.parts = 150
        self.parts_value = self.totmoney / self.parts  # 每份的金额
        self.parts_holding = 0  # 持有份额
        self.latest_buy_bond_yield = 0

    def run(self, date):
        # 获取十年期国债收益率
        if len(self.bond_yield[self.bond_yield["日期"] == date]) > 0:
            bond_yeild = self.bond_yield[self.bond_yield["日期"] == date].iloc[0]["10年"]
            # 根据国债收益率找出对应的持仓表
            if len(self.positions[self.positions["bond_yield"] >= bond_yeild]) > 0:
                positions = self.positions[self.positions["bond_yield"] >= bond_yeild]
                forecast_position = positions.iloc[0]["forecast_position"]  # 获取预期仓位，资金百分比
                if forecast_position != -1:  # -1为正常持有
                    forecast_holding_parts = self.parts * round(forecast_position / 100, 4)
                    diff_parts = self.parts_holding - forecast_holding_parts  # 计算仓位差，已有份额-预期份额
                    if diff_parts == 0:
                        return
                    if diff_parts > 0 and (self.latest_buy_bond_yield - bond_yeild) >= 0.1:  # 需要减仓
                        rem, rem_sum = None, 0
                        if self.code in self.trades:
                            rem = self.trades[self.code].remtable[self.trades[self.code].remtable["date"] <= date].iloc[
                                -1].rem
                            rem_sum = sum([rem[i][1] for i in range(len(rem))])  # 获取最新的仓位总额
                        parts_share = rem_sum / self.parts_holding  # 将持仓份额分为parts_hoding份
                        self.sell(self.code, parts_share * abs(diff_parts), date)
                        self.parts_holding = forecast_holding_parts  # 预期持仓
                        sell_value = \
                            self.trades[self.code].cftable[self.trades[self.code].cftable["date"] <= date].iloc[-1][
                                "cash"]  # 卖出的金额
                        profit = sell_value - self.parts_value * diff_parts  # 收益
                        self.parts_value += profit / self.parts  # 更新每份的金额
                        self.totmoney += sell_value
                        self.latest_buy_bond_yield = int(bond_yeild * 10) / 10  # 更新最近操作的收益率点位
                        print(
                            "sell when 收益率 = %f, 最后操作收益率 = %f, 目前份额 = %f, 预计份额 = %f, 收益 = %f\n" % (
                                bond_yeild, self.latest_buy_bond_yield, self.parts_holding, forecast_holding_parts, profit))
                    elif diff_parts < 0:  # 需要加仓
                        buy_value = self.parts_value * abs(diff_parts)  # 购买金额
                        self.buy(self.code, buy_value, date)
                        self.parts_holding = forecast_holding_parts
                        self.totmoney -= buy_value
                        self.latest_buy_bond_yield = int(bond_yeild * 10) / 10  # 更新最近操作的收益率点位
                        print(
                            "buy when 收益率 = %f, 最后操作收益 = %f, 目前份额 = %f, 预计份额 = %f\n" % (
                                bond_yeild, self.latest_buy_bond_yield, self.parts_holding, forecast_holding_parts))
"""
"""
   计算十年期数据百分位
    pe_cv_size = pe_cv["pe_ttm_ew_cv"].size-1
    pe_cv['PCNT_LIN'] = pe_cv["pe_ttm_ew_cv"].rank(method='max').apply(lambda x: 100.0*(x-1)/pe_cv_size)
    start = 1
    for i in range(2425, len(pe_cv)):
        pe_cv["y10_pe_ew_cvpos"].iloc[i] = (pe_cv["pe_ttm_ew_cv"].iloc[start:i+1].rank(method="max").iloc[-1]-1) * 100.0 / 242500
        start+=1

"""
