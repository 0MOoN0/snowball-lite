import pandas as pd
from pyecharts.charts import Line
from pyecharts import options as opts
from extends.Bucket import Bucket
from extends.Strategy import *
from extends.positions import StockPositions
from xalpha.backtest import BTE
from xalpha.cons import yesterdayobj


class DynamicBalance(BTE):

    def prepare(self):
        self.stock_position = StockPositions().stock_position
        self.parts = 100  # 份额数
        self.part_value = self.totmoney / self.parts  # 每份金额
        self.index_fund_dict = self.kws.get("index_fund_dict")
        index_indicator_dict = self.kws.get("index_indicator_dict")
        stock_record_name = ["date"]
        self.scheduled = self.kws.get("scheduled", None)  # 是否开启定投
        if self.scheduled is not None:
            self.scheduled_value = self.scheduled.get("scheduled_value")
            self.scheduled_date_range = self.scheduled.get("scheduled_date_range")

        self.buckets = {}  # 每个指数对应的数据桶
        self.fund_operation_record = {}
        for index_code in self.index_fund_dict:
            fund_code = self.index_fund_dict[index_code]
            self.set_fund(code="F" + fund_code, dividend_label=1)
            self.buckets[index_code] = Bucket(index_code=index_code,
                                              strategy=ValuationTrendStrategy_V2_2(index_code=index_code,
                                                                                   indicator_column_name=
                                                                                   index_indicator_dict[
                                                                                       index_code],
                                                                                   valuation_reduce=True))
            self.fund_operation_record[index_code] = pd.DataFrame(
                columns=["operation_times", "date", "fund_code", "name", "trade_type", "parts_num", "position",
                         "price"])
            # 指数名称
            part_name = self.stock_position[self.stock_position["index_code"] == index_code]["part"].iloc[0]
            stock_record_name.append(part_name)
        # 仓位记录表
        # self.stock_record = pd.DataFrame(columns=stock_record_name)
        self.stock_record_list = []
        # 操作期数
        self.operation_times = 0

    def run(self, date):
        #  判断是否定投
        if self.scheduled is not None and date in self.scheduled_date_range:
            self.totmoney += self.scheduled_value
            all_stock_holding_parts = sum(self.stock_position["holding_parts"])
            if self.parts - all_stock_holding_parts > 0:
                self.part_value = round(self.totmoney / (self.parts - all_stock_holding_parts), 2)
        need_to_sell = {}
        need_to_buy_dicts = []
        stock_record_dict = {}
        # 对持仓基金进行分拣，分为卖出、买入、持有三类，主要收集卖出、买入两种
        for i, fund in self.stock_position.iterrows():
            bucket = self.buckets[fund["index_code"]]
            # 计算当前基金的持仓百分位
            position = round(fund["holding_parts"] / fund["section_max_position"] * 100, 0)
            point_position, indicator, action = bucket.forecast_position(date, position)
            # 判断仓位差
            if point_position is not None and indicator is not None:
                # 实际的预期仓位
                forcast_position = point_position / 100 * fund["section_max_position"] / 100
                # 预期份额
                forcast_holding_parts = round(forcast_position * self.parts, 0)
                diff_parts = fund["holding_parts"] - forcast_holding_parts  # 当前份额与预期份额的份额差
                if diff_parts > 0 and action == "out":
                    fund_code = self.index_fund_dict[fund["index_code"]]
                    need_to_sell[fund_code] = {"diff_parts": diff_parts, "index_code": fund["index_code"],
                                               "indicator": indicator}
                elif diff_parts < 0 and action == "in":
                    fund_code = self.index_fund_dict[fund["index_code"]]
                    # 判断基金在当前日期是否已经成立
                    if len(self.infos["F" + fund_code].price[self.infos["F" + fund_code].price["date"] <= date]) > 0:
                        need_to_buy_dicts.append(
                            {"fund_code": fund_code, "diff_parts": abs(diff_parts), "index_code": fund["index_code"],
                             "indicator": indicator})
        need_to_buy_df = pd.DataFrame(data=need_to_buy_dicts)
        if len(need_to_sell) > 0 or len(need_to_buy_dicts) > 0:
            stock_record_dict = {"date": date}
        # 卖掉需要出售的份额
        for fund_code in need_to_sell:
            # 查看持仓表是否有该基金
            if self.trades.get("F" + fund_code, None) is None:
                continue
            rem = self.trades["F" + fund_code].remtable[
                self.trades["F" + fund_code].remtable["date"] <= date].iloc[
                -1].rem
            rem_sum = sum([rem[i][1] for i in range(len(rem))])  # 获取最新的仓位总额
            # 获取当前基金所在仓位的索引号
            fund_position_index = self.stock_position[
                self.stock_position["index_code"] == need_to_sell[fund_code]["index_code"]].index
            holding_parts = self.stock_position.loc[fund_position_index, "holding_parts"].iloc[0]
            parts_share = rem_sum / holding_parts
            diff_parts = need_to_sell[fund_code]["diff_parts"]
            # 卖出
            self.sell("F" + fund_code, parts_share * diff_parts, date)
            # 本次卖出的金额
            sold_cash = \
                self.trades["F" + fund_code].cftable[self.trades["F" + fund_code].cftable["date"] == date]["cash"].iloc[
                    0]  # 卖了多少钱
            # 通过计算可支配资金来进行复利投资
            new_holding_parts = holding_parts - diff_parts  # 计算预计仓位
            # 修改持仓表
            self.stock_position.loc[fund_position_index, "holding_parts"] = new_holding_parts
            self.totmoney += sold_cash
            # 持仓份额总和
            all_stock_holding_parts = sum(self.stock_position["holding_parts"])
            # 每一份的金额等于可支配金额 / 可支配份数
            self.part_value = round(self.totmoney / (self.parts - all_stock_holding_parts), 2)
            # 记录持仓变化
            part_name = self.stock_position.loc[fund_position_index, "part"].iloc[0]
            stock_record_dict[part_name] = new_holding_parts
            # 记录单只基金的操作
            index_code = need_to_sell[fund_code]["index_code"]
            # ["operation_times", "date", "fund_code", "name", "trade_type", "parts_num", "price"]
            # 获取基金当前的价格
            prices = self.infos["F" + fund_code].price
            if len(prices[prices["date"] == date]) > 0:
                # 计算当前的持仓百分位
                section_max_position = self.stock_position.loc[fund_position_index, "section_max_position"].iloc[0]
                position_now = round(new_holding_parts / section_max_position * 100, 0)
                price = prices[prices["date"] == date].iloc[0].netvalue
                # price = self.infos["F" + fund_code].price[self.infos["F" + fund_code].price["date"] == date].iloc[0].netvalue
                self.fund_operation_record[index_code] = self.fund_operation_record[index_code].append(
                    {"operation_times": self.operation_times, "date": date, "fund_code": fund_code, "name": part_name,
                     "trade_type": "out", "parts_num": diff_parts, "price": price, "position": position_now},
                    ignore_index=True)
        # 买入份额
        if len(need_to_buy_df) > 0:
            need_to_buy_df.sort_values(by="indicator", inplace=True)
            need_to_buy_df.reset_index(drop=True)
            need_to_buy_df = pd.merge(left=need_to_buy_df, right=self.stock_position, how="left", on="index_code")
        for i, row in need_to_buy_df.iterrows():  # 格式：{"fund_code","diff_parts", "index_code","indicator"}, 类型:series
            category_max_position = row["category_max_position"]
            category = row["category"]
            categorys = self.stock_position[self.stock_position["category"] == category]
            category_holding_parts = categorys["holding_parts"].sum()
            category_max_holding_parts = category_max_position / 100 * self.parts
            if category_holding_parts < category_max_holding_parts:
                if category_holding_parts + row["diff_parts"] > category_max_holding_parts:
                    row["diff_parts"] = category_max_holding_parts - category_holding_parts
                # 获取当前行所在section
                section = row["section"]
                section_max_position = row["section_max_position"]
                sections = self.stock_position[self.stock_position["section"] == section]
                section_holding_parts = sections["holding_parts"].sum()
                section_max_holding_parts = section_max_position / 100 * self.parts
                if section_holding_parts < section_max_holding_parts:  # section未满仓，则加仓
                    buy_parts = row["diff_parts"]
                    if section_holding_parts + row["diff_parts"] > section_max_holding_parts:
                        buy_parts = section_max_holding_parts - section_holding_parts
                    self.buy("F" + row["fund_code"], self.part_value * buy_parts, date)
                    # 购买后的总持仓
                    new_holding_parts = row["holding_parts"] + buy_parts
                    # 获取基金在仓位表对应的索引
                    fund_position_index = self.stock_position[
                        self.stock_position["index_code"] == row["index_code"]].index
                    # 修改持仓表
                    self.stock_position.at[fund_position_index, "holding_parts"] = new_holding_parts
                    self.totmoney -= self.part_value * buy_parts
                    part_name = self.stock_position.loc[fund_position_index, "part"].iloc[0]
                    stock_record_dict[part_name] = new_holding_parts
                    # 记录单只基金的操作
                    index_code = row["index_code"]
                    # ["operation_times", "date", "fund_code", "name", "trade_type", "parts_num", "price"]
                    prices = self.infos["F" + fund_code].price
                    if len(prices[prices["date"] == date]) > 0:
                        position_now = round(new_holding_parts / section_max_position * 100, 0)
                        price = prices[prices["date"] == date].iloc[0].netvalue
                        # price = self.infos["F" + fund_code].price[
                        #     self.infos["F" + fund_code].price["date"] == date].iloc[0].netvalue
                        self.fund_operation_record[index_code] = self.fund_operation_record[index_code].append(
                            {"operation_times": self.operation_times, "date": date, "fund_code": fund_code,
                             "name": part_name,
                             "trade_type": "in", "parts_num": buy_parts, "price": price, "position": position_now},
                            ignore_index=True)
        if len(stock_record_dict) > 1:
            self.operation_times += 1
            self.stock_record_list.append(stock_record_dict)

    def v_tradestatus(self, start=None, end=yesterdayobj(), rendered=True):
        """
        交易状态可视化，显示基金净值，并标记买入点、卖出点、分红点、下折点
        :param start:  开始时间
        :param end:  结束时间
        :param rendered:  是否渲染
        :return:  rendered为False时返回Line对象，为True时渲染图像，默认为渲染图像
        """
        combined_price = pd.DataFrame(columns=["date"])
        for fund_code in self.infos:
            if len(combined_price["date"]) <= len(self.infos[fund_code].price["date"]):
                # 用数据多的表连接数据少的表
                combined_price = self.infos[fund_code].price[["date", "netvalue"]].rename(
                    columns={"netvalue": fund_code}).merge(
                    combined_price, on="date", how="left")
            else:
                combined_price = combined_price.merge(
                    self.infos[fund_code].price[["date", "netvalue"]].rename(columns={"netvalue": fund_code}),
                    on="date", how="left")
        # 对数据进行日期筛选，选择出start到end之间的数据
        p_combined_price = combined_price[combined_price["date"] <= end]
        if start is not None:
            p_combined_price = combined_price[combined_price["date"] >= start]
        # 绘制图像
        line = Line()
        # 添加时间轴
        line.add_xaxis([d.date() for d in p_combined_price.date])
        # 添加基金净值为y轴，并对交易进行标记
        for fund_code in p_combined_price.iloc[:, 1:]:
            # 根据现金流量表制作标记点数据，用于表示买入、卖出、分红，下折
            if self.trades.get(fund_code, None) is None:
                continue
            cftable = self.trades[fund_code].cftable
            pcftable = cftable[cftable["date"] <= end]
            if start is not None:
                pcftable = pcftable[pcftable["date"] >= start]
            upper = pcftable.cash.abs().max()
            lower = pcftable.cash.abs().min()
            if upper == lower:
                upper = 2 * lower + 1  # avoid zero in denominator
            # 标记点的集合
            markers = []
            # 制作标记数据
            for _, row in pcftable.iterrows():
                buy = pcftable[pcftable["date"] <= row.date].iloc[-1]["cash"]
                if buy < 0:
                    color = "#ffff00"
                elif buy == 0:
                    color = "#ff0000"
                else:
                    color = "#3366ff"
                size = (abs(buy) - lower) / (upper - lower) * 5 + 5
                # 获取交易当日净值
                price = p_combined_price[p_combined_price["date"] <= row.date].iloc[-1][fund_code]
                markers.append(opts.MarkPointItem(
                    coord=[row.date.date(), price],
                    itemstyle_opts=opts.ItemStyleOpts(color=color),
                    # this nested itemstyle_opts within MarkPointItem is only supported for pyechart>1.7.1
                    symbol="circle",
                    symbol_size=size,
                ))
            line.add_yaxis(series_name=self.infos[fund_code].name, y_axis=p_combined_price[fund_code].tolist(),
                           is_symbol_show=False, markpoint_opts=opts.MarkPointOpts(
                    data=markers,
                ), label_opts=opts.LabelOpts())
        line.set_global_opts(
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=True, type_="slider", range_start=50, range_end=100
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    type_="slider",
                    orient="vertical",
                    range_start=50,
                    range_end=100,
                ),
            ],
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                trigger="axis",
                trigger_on="mousemove",
                axis_pointer_type="cross",
            ),
            yaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(is_show=True),
                is_scale=True,
            ),
        )
        if rendered:
            return line.render_notebook()
        else:
            return line


class ValuationTrend(BTE):
    """
    基于估值与趋势的单基金投资策略，估值买入，估值+趋势卖出
    """

    def prepare(self):
        # 获取近十年PE数据
        self.code = self.kws["code"]
        self.valuation_reduce = self.kws.get("valuation_reduce", True)
        self.index_code = self.kws["index_code"]
        self.indicator_column_name = self.kws["indicator_column_name"]
        self.data = pd.read_csv(
            "I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\index_" + self.index_code + "_data.csv", index_col=0,
            header=0,
            encoding="gbk")
        self.data["date"] = pd.to_datetime(self.data["date"])
        self.set_fund(code=self.code, dividend_label=1)
        self.ref_indicator = self.data[["date", self.indicator_column_name]]
        self.holding_parts = 0  # 持有份数
        self.position = StockPositions()  # 仓位表
        self.parts = 100  # 份额数
        self.part_value = self.totmoney / self.parts  # 每份金额
        self.trend_sell = False  # 是否到达75百分位

    def run(self, date):
        # 判断指标
        indicator = int(
            round(self.ref_indicator[self.ref_indicator["date"] == date][self.indicator_column_name].iloc[0], 2) * 100)
        if indicator <= 30 and self.holding_parts < self.parts:  # 在没有满仓的前提下加仓
            self.trend_sell = False
            buy_position = self.position.buy_position[self.position.buy_position["indicator"] <= indicator]  # 买入的仓位表
            if len(buy_position) > 0:
                instep = buy_position["instep"].iloc[0]  # 每次买入的份额步长因子
                forecast_position = buy_position["position"].iloc[0]  # 预期仓位
                ref_indicator = buy_position["indicator"].iloc[0]
                forecast_holding_parts = (forecast_position - (indicator - ref_indicator) * instep) / 100 * self.parts
                # forecast_holding_parts = forecast_position / 100 * self.parts + (ref_indicator - indicator + 1) * instep
                forecast_holding_parts = int(round(forecast_holding_parts, 0))
                if forecast_holding_parts <= self.holding_parts:  # 预期持有份额大于现在持有份额，基金这时可能处于上涨状态，选择持有份额
                    return
                diff_parts = forecast_holding_parts - self.holding_parts
                self.buy(self.code, self.part_value * diff_parts, date)
                self.holding_parts = forecast_holding_parts
                self.totmoney -= self.part_value * diff_parts
                print("持仓份数===%d" % (self.holding_parts))
        elif indicator >= 75 or self.trend_sell and self.holding_parts > 0:  # 在有剩余仓位的前提下减仓
            self.trend_sell = True
            data_before_3 = self.data[self.data["date"] < date][["ma_51", "ma_20", "cp"]].tail(3)  # 获取三天前的数据
            # 如果有效跌破60日均线，减仓到2成，跌破20日均线，减仓到5成
            reduce_factor = 0.2 if ((data_before_3["ma_51"] - data_before_3["cp"]) > 0).all() else 0.5 if (
                    (data_before_3["ma_20"] - data_before_3["cp"]) > 0).all() else -1
            if reduce_factor > 0:  # 如果有效跌破指标。则减仓到5成或2成
                forecast_holding_parts = int(round(reduce_factor * self.parts, 0))  # 预期仓位
                diff_parts = forecast_holding_parts - self.holding_parts
                if diff_parts >= 0:  # 持有份额不够预期仓位，不减仓
                    return
                # 按比例赎回
                if self.code in self.trades:
                    rem = self.trades[self.code].remtable[self.trades[self.code].remtable["date"] <= date].iloc[
                        -1].rem
                    rem_sum = sum([rem[i][1] for i in range(len(rem))])  # 获取最新的仓位总额
                    # 计算平均成本（包含费用）：申购现金总额 / 份额
                parts_share = rem_sum / self.holding_parts  # 将持仓份额分为parts_hoding份
                self.sell(self.code, parts_share * diff_parts, date)
                # 获取卖出份额
                sold_cash = \
                    self.trades[self.code].cftable[self.trades[self.code].cftable["date"] == date]["cash"].iloc[0]
                # 模拟现实，通过计算可支配资金来进行复利投资
                self.holding_parts = forecast_holding_parts
                self.totmoney += sold_cash
                # 每一份的金额等于可支配金额 / 可支配份数
                self.part_value = self.totmoney / (self.parts - self.holding_parts)
                if reduce_factor == 0.2:
                    self.trend_sell = False
                print("持仓份数===%d" % (self.holding_parts))
                return
            # 根据估值百分位减仓
            if self.valuation_reduce:
                sell_position = self.position.sell_position[self.position.sell_position["indicator"] >= indicator]
                if len(sell_position) > 0:
                    outstep = sell_position["outstep"].iloc[0]  # 每次减仓的份数步长因子
                    diff_indicator = sell_position["indicator"].iloc[0] - indicator  # 指标差
                    # 预期持仓份额
                    forecast_holding_parts = diff_indicator * outstep + int(
                        round(sell_position["remain_position"].iloc[0] * self.parts / 100, 0))
                    diff_parts = self.holding_parts - forecast_holding_parts
                    if diff_parts <= 0:  # 当实际持仓与预计持仓份数相等或者实际持仓比预计持仓份数小时，不用进行卖出操作
                        return
                    if self.code in self.trades:
                        rem = self.trades[self.code].remtable[self.trades[self.code].remtable["date"] <= date].iloc[
                            -1].rem
                        rem_sum = sum([rem[i][1] for i in range(len(rem))])  # 获取最新的仓位总额
                        # 计算平均成本（包含费用）：申购现金总额 / 份额
                    parts_share = rem_sum / self.holding_parts  # 将持仓份额分为parts_hoding份
                    self.sell(self.code, parts_share * diff_parts, date)
                    # 获取卖出份额
                    sold_cash = \
                        self.trades[self.code].cftable[self.trades[self.code].cftable["date"] <= date]["cash"].iloc[-1]
                    # 计算收益
                    self.holding_parts = forecast_holding_parts
                    # 模拟现实，通过计算可支配资金来进行复利投资
                    self.totmoney += sold_cash
                    # 每一份的金额等于可支配金额 / 可支配份数
                    self.part_value = self.totmoney / (self.parts - self.holding_parts)
                    print("持仓份数===%d" % (self.holding_parts))
