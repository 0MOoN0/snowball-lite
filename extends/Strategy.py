import numpy as np
import pandas as pd
import py_script.data_process as dp


class Strategy():

    def __init__(self, strategy_name="基础策略"):
        self.strategy_name = strategy_name

    def operate(self):
        raise BaseException("需要初始化策略操作")


class BasicStrategy(Strategy):
    """
    基础策略类，包含估值买入和估值+趋势卖出策略
    """

    def __init__(self, index_code, indicator_column_name, valuation_reduce=True):
        arr_indicator = np.array([30, 20, 10, 5, 2, 1, 0])  # 0, 2, 5, 10, 20, 30
        arr_position = np.array([1, 10, 30, 50, 70, 80, 100])  # 100, 80, 70, 50, 30, 10
        arr_instep = np.array([1, 1, 2, 4, 6, 10, 20])  # 0, 5, 6, 4, 2, 1
        self.buy_position = pd.DataFrame(data=np.vstack((arr_indicator, arr_position, arr_instep)).T,
                                         columns=["indicator", "position", "instep"])
        # 卖出分位数
        arr_indicator = np.array([75, 80, 85, 90, 95, 100])
        arr_position = np.array([90, 80, 60, 40, 20, 0])
        arr_outstep = np.array([2, 2, 4, 4, 4, 0])
        self.sell_position = pd.DataFrame(data=np.vstack((arr_indicator, arr_position, arr_outstep)).T,
                                          columns=["indicator", "remain_position", "outstep"])
        self.indicator_column_name = indicator_column_name
        self.valuation_reduce = valuation_reduce
        # 加载指数数据
        self.index_data = pd.read_csv(
            "I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\index_" + index_code + "_data.csv",
            index_col=0, header=0)
        # 获取MACD指标
        self.index_macd = dp.get_indicator_macd(index_data=self.index_data)
        # 剔除指标列有Nan的数据
        self.index_data.dropna(axis=0, how="any", inplace=True, subset=[self.indicator_column_name])
        # 转换日期
        self.index_data["date"] = pd.to_datetime(self.index_data["date"])
        self.ref_indicator = self.index_data[["date", self.indicator_column_name]]
        self.trend_sell = False  # 是否到达75百分位
        super().__init__(strategy_name="基础估值趋势策略")

    def operate(self, date):
        """
        根据指数数据判断预期仓位
        :param:    date, 要进行计算仓位的当天
        :return:   tuple, 第一个值为预期仓位百分数，第二个值为当前估值百分位
        """
        # 判断指标
        part_data = self.ref_indicator[self.ref_indicator["date"] == date][self.indicator_column_name]
        if len(part_data) == 0:
            return None, None, None
        indicator = int(round(part_data.iloc[0], 2) * 100)
        if indicator <= 30:
            self.trend_sell = False
            buy_position = self.buy_position[self.buy_position["indicator"] <= indicator]  # 买入的仓位表
            if len(buy_position) > 0:
                instep = buy_position["instep"].iloc[0]  # 每次买入的份额步长因子
                forecast_position = buy_position["position"].iloc[0]  # 预期仓位
                ref_indicator = buy_position["indicator"].iloc[0]
                forecast_position = forecast_position - (indicator - ref_indicator) * instep
                return forecast_position, indicator, "in"
        elif indicator >= 75 or self.trend_sell:
            self.trend_sell = True
            data_before_3 = self.index_data[self.index_data["date"] < date][["ma_51", "ma_20", "cp"]].tail(
                3)  # 获取三天前的数据
            reduce_factor = 0.2 if ((data_before_3["ma_51"] - data_before_3["cp"]) > 0).all() else 0.5 if (
                    (data_before_3["ma_20"] - data_before_3["cp"]) > 0).all() else -1
            if reduce_factor > 0:
                if reduce_factor == 0.2:
                    self.trend_sell = False
                return reduce_factor * 100, indicator, "out"  # 趋势减仓
            if self.valuation_reduce:  # 估值减仓
                sell_position = self.sell_position[self.sell_position["indicator"] >= indicator]
                if len(sell_position) > 0:
                    outstep = sell_position["outstep"].iloc[0]
                    diff_indicator = sell_position["indicator"].iloc[0] - indicator  # 指标差
                    forecast_position = sell_position["remain_position"].iloc[0] + diff_indicator * outstep
                    return forecast_position, indicator, "out"
        return None, None, None


class ValuationTrendStrategy(Strategy):
    """
    基于BasicStrategy的估值趋势类，包含估值+趋势买入策略和估值+趋势卖出策略
    修改部分：1. 估值买入部分仓位最大为80， 剩下20仓位为趋势仓位
    """

    def __init__(self, index_code, indicator_column_name, valuation_reduce=True):
        arr_indicator = np.array([30, 20, 10, 5, 2, 1, 0])  # 0, 2, 5, 10, 20, 30
        arr_position = np.array([1, 10, 20, 30, 50, 65, 80])  # 100, 80, 70, 50, 30, 10
        arr_instep = np.array([1, 1, 1, 2, 6, 15, 15])  # 0, 5, 6, 4, 2, 1
        self.buy_position = pd.DataFrame(data=np.vstack((arr_indicator, arr_position, arr_instep)).T,
                                         columns=["indicator", "position", "instep"])
        # 卖出分位数
        arr_indicator = np.array([75, 80, 85, 90, 95, 100])
        arr_position = np.array([90, 80, 60, 40, 20, 0])
        arr_outstep = np.array([2, 2, 4, 4, 4, 0])
        self.sell_position = pd.DataFrame(data=np.vstack((arr_indicator, arr_position, arr_outstep)).T,
                                          columns=["indicator", "remain_position", "outstep"])
        self.indicator_column_name = indicator_column_name
        self.valuation_reduce = valuation_reduce
        # 加载指数数据
        self.index_data = pd.read_csv(
            "I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\index_" + index_code + "_data.csv",
            index_col=0, header=0)
        # 获取MACD指标
        self.index_macd = dp.get_indicator_macd(index_data=self.index_data)
        # 剔除指标列有Nan的数据
        self.index_data.dropna(axis=0, how="any", inplace=True, subset=[self.indicator_column_name])
        self.index_data["date"] = pd.to_datetime(self.index_data["date"])
        self.ref_indicator = self.index_data[["date", self.indicator_column_name]]
        self.trend_sell = False  # 是否到达75百分位
        self.trend_buy = False
        self.index_code = index_code
        super().__init__(strategy_name="基础估值趋势策略")

    def operate(self, date, position):
        """
        根据指数数据判断预期仓位
        :param:    date, 要进行计算仓位的当天
        :return:   tuple, 第一个值为预期仓位百分数，第二个值为当前估值百分位
        """
        # 判断指标
        part_data = self.ref_indicator[self.ref_indicator["date"] == date][self.indicator_column_name]
        # 使用百分位做指标之前要有一定的数据量，否则没那么准确
        if len(part_data) == 0 or len(self.ref_indicator[self.ref_indicator["date"] <= date]) <= 200:
            return None, None, None
        indicator = int(round(part_data.iloc[0], 2) * 100)
        if indicator <= 30:
            self.trend_sell = False
            # 判断是否进行趋势加仓
            if self.trend_buy and position >= 80:  # 趋势加仓部分

                # 获取两日的中长期均线并判断
                """  通过均线指标判断
                data_before_3 = self.index_data[self.index_data["date"] < date][
                    ["ma_51", "ma_20", "ma_120", "cp"]].tail(3)
                # 短期均线趋势: 1.中短期均线向上  2.收盘点在中长线上
                if (data_before_3["ma_20"].pct_change().fillna(0) >= 0).all() \
                        and (
                        (data_before_3["cp"] > data_before_3["ma_51"]).all() and (
                        data_before_3["cp"] > data_before_3["ma_20"])).all() \
                        and (data_before_3["cp"] > data_before_3["ma_120"]).all() \
                        and (data_before_3["ma_20"] > data_before_3["ma_51"]).all():
                    if (data_before_3["ma_20"] > data_before_3["ma_120"]).all():
                        return 100, indicator, "in"
                    return 90, indicator, "in"
                """
                # 判断指标是否黏连
                macd_data = self.index_macd[self.index_macd["date"] < date]
                if len(macd_data) >= 3:
                    # 根据柱状图数据的50分位数来判断是否黏连
                    sticky_indicator = np.percentile(macd_data["MACD_OSC_12_26"], 50)
                    if not (abs(macd_data.tail(3)["MACD_OSC_12_26"]) < abs(sticky_indicator)).all():
                        # 非黏连，判断DIF线和DEA线，金叉时买入
                        if macd_data.iloc[-1]["MACD_DIFF_12_26"] > macd_data.iloc[-1]["MACD_DEM_12_26"] \
                                and macd_data.iloc[-2]["MACD_DIFF_12_26"] < macd_data.iloc[-2]["MACD_DEM_12_26"]:
                            return 100, indicator, "in"

            buy_position = self.buy_position[self.buy_position["indicator"] <= indicator]  # 买入的仓位表
            if len(buy_position) > 0:
                instep = buy_position["instep"].iloc[0]  # 每次买入的份额步长因子
                forecast_position = buy_position["position"].iloc[0]  # 预期仓位
                ref_indicator = buy_position["indicator"].iloc[0]
                forecast_position = forecast_position - (indicator - ref_indicator) * instep
                if len(buy_position) == 1:
                    self.trend_buy = True
                return forecast_position, indicator, "in"
            # or self.trend_sell
        elif indicator >= 75:
            self.trend_sell = True
            self.trend_buy = False
            data_before_3 = self.index_data[self.index_data["date"] < date][["ma_51", "ma_20", "cp"]].tail(
                3)  # 获取三天前的数据
            reduce_factor = 0.2 if ((data_before_3["ma_51"] - data_before_3["cp"]) > 0).all() else 0.5 if (
                    (data_before_3["ma_20"] - data_before_3["cp"]) > 0).all() else -1
            if reduce_factor > 0:
                if reduce_factor == 0.2:
                    self.trend_sell = False
                return reduce_factor * 100, indicator, "out"  # 趋势减仓
            if self.valuation_reduce:  # 估值减仓
                sell_position = self.sell_position[self.sell_position["indicator"] >= indicator]
                if len(sell_position) > 0:
                    outstep = sell_position["outstep"].iloc[0]
                    diff_indicator = sell_position["indicator"].iloc[0] - indicator  # 指标差
                    forecast_position = sell_position["remain_position"].iloc[0] + diff_indicator * outstep
                    return forecast_position, indicator, "out"
        return None, None, None


class ValuationTrendStrategy_V2_2(Strategy):
    """
    基于估值和均线趋势的策略，主要是买入方面的变化，分两个仓位，估值仓位和趋势仓位，估值仓位由估值百分位*买入份额因子决定买入的份额，趋势仓位由短均线穿越长均线时买入
    """

    def __init__(self, index_code, indicator_column_name, valuation_reduce=True):
        arr_indicator = np.array([30, 20, 10, 5, 2, 1, 0])  # 0, 2, 5, 10, 20, 30
        arr_position = np.array([1, 10, 20, 30, 50, 65, 80])  # 100, 80, 70, 50, 30, 10
        arr_instep = np.array([1, 1, 1, 2, 6, 15, 15])  # 0, 5, 6, 4, 2, 1
        self.buy_position = pd.DataFrame(data=np.vstack((arr_indicator, arr_position, arr_instep)).T,
                                         columns=["indicator", "position", "instep"])
        # 卖出分位数
        arr_indicator = np.array([75, 80, 85, 90, 95, 100])
        arr_position = np.array([90, 80, 60, 40, 20, 0])
        arr_outstep = np.array([2, 2, 4, 4, 4, 0])
        self.sell_position = pd.DataFrame(data=np.vstack((arr_indicator, arr_position, arr_outstep)).T,
                                          columns=["indicator", "remain_position", "outstep"])
        self.indicator_column_name = indicator_column_name
        self.valuation_reduce = valuation_reduce
        # 加载指数数据
        self.index_data = pd.read_csv(
            "I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\index_" + index_code + "_data.csv",
            index_col=0, header=0)
        # 获取MACD指标
        self.index_macd = dp.get_indicator_macd(index_data=self.index_data)
        # 剔除指标列有Nan的数据
        self.index_data.dropna(axis=0, how="any", inplace=True, subset=[self.indicator_column_name])
        self.index_data["date"] = pd.to_datetime(self.index_data["date"])
        self.ref_indicator = self.index_data[["date", self.indicator_column_name]]
        self.trend_sell = False  # 是否到达75百分位
        self.trend_buy = False
        self.index_code = index_code
        super().__init__(strategy_name="基础估值趋势策略")

    def operate(self, date, position):
        """
        根据指数数据判断预期仓位
        :param:    date, 要进行计算仓位的当天
        :return:   tuple, 第一个值为预期仓位百分数，第二个值为当前估值百分位
        """
        # 判断指标
        part_data = self.ref_indicator[self.ref_indicator["date"] == date][self.indicator_column_name]
        # 使用百分位做指标之前要有一定的数据量，否则没那么准确
        if len(part_data) == 0 or len(self.ref_indicator[self.ref_indicator["date"] <= date]) <= 200:
            return None, None, None
        indicator = int(round(part_data.iloc[0], 2) * 100)
        if indicator <= 30:
            self.trend_sell = False
            # 判断是否进行趋势加仓
            if self.trend_buy:  # 趋势加仓部分 and position >= 80

                # 获取两日的中长期均线并判断
                # 通过均线指标判断
                data_before_3 = self.index_data[self.index_data["date"] < date][
                    ["ma_51", "ma_20", "ma_120", "cp"]].tail(3)
                # 短期均线趋势: 1.中短期均线向上  2.收盘点在中长线上
                if (data_before_3["ma_20"].pct_change().fillna(0) >= 0).all() \
                        and (
                        (data_before_3["cp"] > data_before_3["ma_51"]).all() and (
                        data_before_3["cp"] > data_before_3["ma_20"])).all() \
                        and (data_before_3["cp"] > data_before_3["ma_120"]).all() \
                        and (data_before_3["ma_20"] > data_before_3["ma_51"]).all():
                    if (data_before_3["ma_20"] > data_before_3["ma_120"]).all():
                        return 100, indicator, "in"
                    return 90, indicator, "in"
            buy_position = self.buy_position[self.buy_position["indicator"] <= indicator]  # 买入的仓位表
            if len(buy_position) > 0:
                instep = buy_position["instep"].iloc[0]  # 每次买入的份额步长因子
                forecast_position = buy_position["position"].iloc[0]  # 预期仓位
                ref_indicator = buy_position["indicator"].iloc[0]
                forecast_position = forecast_position - (indicator - ref_indicator) * instep
                if len(buy_position) == 1:
                    self.trend_buy = True
                return forecast_position, indicator, "in"
            # or self.trend_sell
        elif indicator >= 75:
            self.trend_sell = True
            self.trend_buy = False
            data_before_3 = self.index_data[self.index_data["date"] < date][["ma_51", "ma_20", "cp"]].tail(
                3)  # 获取三天前的数据
            reduce_factor = 0.2 if ((data_before_3["ma_51"] - data_before_3["cp"]) > 0).all() else 0.5 if (
                    (data_before_3["ma_20"] - data_before_3["cp"]) > 0).all() else -1
            if reduce_factor > 0:
                if reduce_factor == 0.2:
                    self.trend_sell = False
                return reduce_factor * 100, indicator, "out"  # 趋势减仓
            if self.valuation_reduce:  # 估值减仓
                sell_position = self.sell_position[self.sell_position["indicator"] >= indicator]
                if len(sell_position) > 0:
                    outstep = sell_position["outstep"].iloc[0]
                    diff_indicator = sell_position["indicator"].iloc[0] - indicator  # 指标差
                    forecast_position = sell_position["remain_position"].iloc[0] + diff_indicator * outstep
                    return forecast_position, indicator, "out"
        return None, None, None


class ValuationTrendStrategy_V2_4(ValuationTrendStrategy):
    """
    V2_4版策略，V2是ETF组合投资，4是迭代的第四版，主要是修改买入规则，将具体的买入时机交给趋势
    第4版的区别：前面几版是按照估值进行购买的，这版将加重趋势投资的权重，将买入的范围交给估值，买入的时机交给趋势，目前这版将会是右侧交易
    趋势指标使用MACD周K
    """

    def __init__(self, index_code, indicator_column_name, valuation_reduce=True):

        super().__init__(index_code, indicator_column_name, valuation_reduce=valuation_reduce)

    def operate(self, date, position):
        """
        根据指数数据判断预期仓位
        :param:    date, 要进行计算仓位的当天
        :return:   tuple, 第一个值为预期仓位百分数，第二个值为当前估值百分位
        """
        # 判断指标
        part_data = self.ref_indicator[self.ref_indicator["date"] == date][self.indicator_column_name]
        # 使用百分位做指标之前要有一定的数据量，否则没那么准确
        if len(part_data) == 0 or len(self.ref_indicator[self.ref_indicator["date"] <= date]) <= 200:
            return None, None, None
        indicator = int(round(part_data.iloc[0], 2) * 100)
        if indicator <= 30:
            self.trend_sell = False
            macd_data = self.index_macd[self.index_macd["date"] < date]
            if len(macd_data) >= 3:
                # 黏连指标，用于判断MACD是否黏连
                sticky_indicator = np.percentile(macd_data["MACD_OSC_12_26"], 50)
                # 根据柱状图数据的50分位数来判断是否黏连
                if not (abs(macd_data.tail(3)["MACD_OSC_12_26"]) < abs(sticky_indicator)).all():
                    # 判断是否金叉
                    if macd_data.iloc[-1]["MACD_DIFF_12_26"] > macd_data.iloc[-1]["MACD_DEM_12_26"] \
                            and macd_data.iloc[-2]["MACD_DIFF_12_26"] < macd_data.iloc[-2]["MACD_DEM_12_26"]:
                        # 判断当前是否为趋势仓位
                        if self.trend_buy and position >= 80:
                            return 100, indicator, "in"
                        buy_position = self.buy_position[self.buy_position["indicator"] <= indicator]  # 买入的仓位表
                        if len(buy_position) > 0:
                            instep = buy_position["instep"].iloc[0]  # 每次买入的份额步长因子
                            forecast_position = buy_position["position"].iloc[0]  # 预期仓位
                            ref_indicator = buy_position["indicator"].iloc[0]
                            forecast_position = forecast_position - (indicator - ref_indicator) * instep
                            if len(buy_position) == 1:
                                self.trend_buy = True
                            return forecast_position, indicator, "in"
            # 判断是否进行趋势加仓
            # if self.trend_buy and position >= 80:  # 取值加仓后的趋势加仓部分，2成仓位
            #     # 判断指标是否黏连
            #     macd_data = self.index_macd[self.index_macd["date"] < date]
            #     if len(macd_data) >= 3:
            #         # 根据柱状图数据的50分位数来判断是否黏连
            #         sticky_indicator = np.percentile(macd_data["MACD_OSC_12_26"], 50)
            #         if not (abs(macd_data.tail(3)["MACD_OSC_12_26"]) < abs(sticky_indicator)).all():
            #             # 非黏连，判断DIF线和DEA线，金叉时买入
            #             if macd_data.iloc[-1]["MACD_DIFF_12_26"] > macd_data.iloc[-1]["MACD_DEM_12_26"] \
            #                     and macd_data.iloc[-2]["MACD_DIFF_12_26"] < macd_data.iloc[-2]["MACD_DEM_12_26"]:
            #                 return 100, indicator, "in"
            # or self.trend_sell
        elif indicator >= 75:
            self.trend_sell = True
            self.trend_buy = False
            data_before_3 = self.index_data[self.index_data["date"] < date][["ma_51", "ma_20", "cp"]].tail(
                3)  # 获取三天前的数据
            reduce_factor = 0.2 if ((data_before_3["ma_51"] - data_before_3["cp"]) > 0).all() else 0.5 if (
                    (data_before_3["ma_20"] - data_before_3["cp"]) > 0).all() else -1
            if reduce_factor > 0:
                if reduce_factor == 0.2:
                    self.trend_sell = False
                return reduce_factor * 100, indicator, "out"  # 趋势减仓
            if self.valuation_reduce:  # 估值减仓
                sell_position = self.sell_position[self.sell_position["indicator"] >= indicator]
                if len(sell_position) > 0:
                    outstep = sell_position["outstep"].iloc[0]
                    diff_indicator = sell_position["indicator"].iloc[0] - indicator  # 指标差
                    forecast_position = sell_position["remain_position"].iloc[0] + diff_indicator * outstep
                    return forecast_position, indicator, "out"
        return None, None, None


class ValuationTrendStrategy_V2_5(ValuationTrendStrategy):
    """
    V2_5版策略， 在V2_4的基础上进行变化，提高估值交易的比重，也就是左侧仓位，当估值遇到预计持仓表时预期估值时，买入持仓表对应的仓位，其余仓位使用趋势判断
    """

    def __init__(self, index_code, indicator_column_name, valuation_reduce=True):
        super().__init__(index_code, indicator_column_name, valuation_reduce=valuation_reduce)

    def operate(self, date, position):
        """
        根据指数数据判断预期仓位
        :param:    date, 要进行计算仓位的当天
        :return:   tuple, 第一个值为预期仓位百分数，第二个值为当前估值百分位
        """
        # 判断指标
        part_data = self.ref_indicator[self.ref_indicator["date"] == date][self.indicator_column_name]
        # 使用百分位做指标之前要有一定的数据量，否则没那么准确
        if len(part_data) == 0 or len(self.ref_indicator[self.ref_indicator["date"] <= date]) <= 200:
            return None, None, None
        indicator = int(round(part_data.iloc[0], 2) * 100)
        if indicator <= 30:
            self.trend_sell = False
            buy_position = self.buy_position[self.buy_position["indicator"] <= indicator]  # 买入的仓位表
            last_indicator = buy_position.iloc[0]["indicator"]
            # 如果当前指标正等于预期指标，且最后的趋势仓位并未买满，买入预期指标对应的预期仓位
            if indicator == last_indicator and position < 80:
                instep = buy_position["instep"].iloc[0]  # 每次买入的份额步长因子
                forecast_position = buy_position["position"].iloc[0]  # 预期仓位
                ref_indicator = buy_position["indicator"].iloc[0]
                forecast_position = forecast_position - (indicator - ref_indicator) * instep
                return forecast_position, indicator, "in"
            # 判断指标是否黏连
            macd_data = self.index_macd[self.index_macd["date"] < date]
            if len(macd_data) >= 3:
                # 根据柱状图数据的50分位数来判断是否黏连
                sticky_indicator = np.percentile(macd_data["MACD_OSC_12_26"], 50)
                if not (abs(macd_data.tail(3)["MACD_OSC_12_26"]) < abs(sticky_indicator)).all():
                    # 非黏连，判断DIF线和DEA线，金叉时买入
                    if macd_data.iloc[-1]["MACD_DIFF_12_26"] > macd_data.iloc[-1]["MACD_DEM_12_26"] \
                            and macd_data.iloc[-2]["MACD_DIFF_12_26"] < macd_data.iloc[-2]["MACD_DEM_12_26"]:
                        # 如果是最后的趋势仓位，则买入最后的趋势仓位
                        if position >= 80:
                            return 100, indicator, "in"
                        # 根据金叉所在的指标分位数买入对应的仓位
                        instep = buy_position["instep"].iloc[0]  # 每次买入的份额步长因子
                        forecast_position = buy_position["position"].iloc[0]  # 预期仓位
                        ref_indicator = buy_position["indicator"].iloc[0]
                        forecast_position = forecast_position - (indicator - ref_indicator) * instep
                        if len(buy_position) == 1:
                            self.trend_buy = True
                        return forecast_position, indicator, "in"
        elif indicator >= 75:
            self.trend_sell = True
            self.trend_buy = False
            data_before_3 = self.index_data[self.index_data["date"] < date][["ma_51", "ma_20", "cp"]].tail(
                3)  # 获取三天前的数据
            reduce_factor = 0.2 if ((data_before_3["ma_51"] - data_before_3["cp"]) > 0).all() else 0.5 if (
                    (data_before_3["ma_20"] - data_before_3["cp"]) > 0).all() else -1
            if reduce_factor > 0:
                if reduce_factor == 0.2:
                    self.trend_sell = False
                return reduce_factor * 100, indicator, "out"  # 趋势减仓
            if self.valuation_reduce:  # 估值减仓
                sell_position = self.sell_position[self.sell_position["indicator"] >= indicator]
                if len(sell_position) > 0:
                    outstep = sell_position["outstep"].iloc[0]
                    diff_indicator = sell_position["indicator"].iloc[0] - indicator  # 指标差
                    forecast_position = sell_position["remain_position"].iloc[0] + diff_indicator * outstep
                    return forecast_position, indicator, "out"
        return None, None, None


class ValuationTrendStrategy_V2_6(ValuationTrendStrategy):
    """
    V2_6版策略， 在V2_5的基础上进行变化，改变卖出策略，使用十年期PE/PB分位数的平均值卖出
    """

    def __init__(self, index_code, indicator_column_name, valuation_reduce=True):
        super().__init__(index_code, indicator_column_name, valuation_reduce=valuation_reduce)

    def operate(self, date, position):
        """
        根据指数数据判断预期仓位
        :param:    date, 要进行计算仓位的当天
        :return:   tuple, 第一个值为预期仓位百分数，第二个值为当前估值百分位
        """
        # 判断指标
        part_data = self.ref_indicator[self.ref_indicator["date"] == date][self.indicator_column_name]
        # 使用百分位做指标之前要有一定的数据量，否则没那么准确
        if len(part_data) == 0 or len(self.ref_indicator[self.ref_indicator["date"] <= date]) <= 200:
            return None, None, None
        indicator = int(round(part_data.iloc[0], 2) * 100)
        # 卖出的指标
        index_data = self.index_data[self.index_data["date"] == date]
        if len(index_data) > 0:
            if index_data.iloc[0]["y10_pe_ttm_fs_ewpvo_cvpos"] is np.nan and index_data.iloc[0][
                "y10_pb_fs_ew_cvpos"] is np.nan:
                return None, None, None
            elif index_data.iloc[0]["y10_pe_ttm_fs_ewpvo_cvpos"] is np.nan:
                sold_out_indicator = index_data.iloc[0]["y10_pb_fs_ew_cvpos"]
            elif index_data.iloc[0]["y10_pb_fs_ew_cvpos"] is np.nan:
                sold_out_indicator = index_data.iloc[0]["y10_pe_ttm_fs_ewpvo_cvpos"]
            else:
                sold_out_indicator = (index_data.iloc[0]["y10_pb_fs_ew_cvpos"] + index_data.iloc[0][
                    "y10_pe_ttm_fs_ewpvo_cvpos"]) / 2
        if indicator <= 30:
            self.trend_sell = False
            buy_position = self.buy_position[self.buy_position["indicator"] <= indicator]  # 买入的仓位表
            last_indicator = buy_position.iloc[0]["indicator"]
            # 如果当前指标正等于预期指标，且最后的趋势仓位并未买满，买入预期指标对应的预期仓位
            if indicator == last_indicator and position < 80:
                instep = buy_position["instep"].iloc[0]  # 每次买入的份额步长因子
                forecast_position = buy_position["position"].iloc[0]  # 预期仓位
                ref_indicator = buy_position["indicator"].iloc[0]
                forecast_position = forecast_position - (indicator - ref_indicator) * instep
                return forecast_position, indicator, "in"
            # 判断指标是否黏连
            macd_data = self.index_macd[self.index_macd["date"] < date]
            if len(macd_data) >= 3:
                # 根据柱状图数据的50分位数来判断是否黏连
                sticky_indicator = np.percentile(macd_data["MACD_OSC_12_26"], 50)
                if not (abs(macd_data.tail(3)["MACD_OSC_12_26"]) < abs(sticky_indicator)).all():
                    # 非黏连，判断DIF线和DEA线，金叉时买入
                    if macd_data.iloc[-1]["MACD_DIFF_12_26"] > macd_data.iloc[-1]["MACD_DEM_12_26"] \
                            and macd_data.iloc[-2]["MACD_DIFF_12_26"] < macd_data.iloc[-2]["MACD_DEM_12_26"]:
                        # 如果是最后的趋势仓位，则买入最后的趋势仓位
                        if position >= 80:
                            return 100, indicator, "in"
                        # 根据金叉所在的指标分位数买入对应的仓位
                        instep = buy_position["instep"].iloc[0]  # 每次买入的份额步长因子
                        forecast_position = buy_position["position"].iloc[0]  # 预期仓位
                        ref_indicator = buy_position["indicator"].iloc[0]
                        forecast_position = forecast_position - (indicator - ref_indicator) * instep
                        if len(buy_position) == 1:
                            self.trend_buy = True
                        return forecast_position, indicator, "in"
            # or self.trend_sell
        elif sold_out_indicator >= 75:
            indicator = sold_out_indicator
            self.trend_sell = True
            self.trend_buy = False
            data_before_3 = self.index_data[self.index_data["date"] < date][["ma_51", "ma_20", "cp"]].tail(
                3)  # 获取三天前的数据
            reduce_factor = 0.2 if ((data_before_3["ma_51"] - data_before_3["cp"]) > 0).all() else 0.5 if (
                    (data_before_3["ma_20"] - data_before_3["cp"]) > 0).all() else -1
            if reduce_factor > 0:
                if reduce_factor == 0.2:
                    self.trend_sell = False
                return reduce_factor * 100, indicator, "out"  # 趋势减仓
            if self.valuation_reduce:  # 估值减仓
                sell_position = self.sell_position[self.sell_position["indicator"] >= indicator]
                if len(sell_position) > 0:
                    outstep = sell_position["outstep"].iloc[0]
                    diff_indicator = sell_position["indicator"].iloc[0] - indicator  # 指标差
                    forecast_position = sell_position["remain_position"].iloc[0] + diff_indicator * outstep
                    return forecast_position, indicator, "out"
        return None, None, None


class ValuationTrendStrategy_V2_7(Strategy):
    """
    基于估值和均线趋势的策略，分两个仓位，估值仓位和趋势仓位，估值仓位由估值百分位*买入份额因子决定买入的份额，趋势仓位由短均线穿越长均线时买入
    2_7基于2_2策略，对卖出部分进行策略变化，卖出由十年期PE和PB的平均值决定
    """

    def __init__(self, index_code, indicator_column_name, valuation_reduce=True):
        arr_indicator = np.array([30, 20, 10, 5, 2, 1, 0])  # 0, 2, 5, 10, 20, 30
        arr_position = np.array([1, 10, 20, 30, 50, 65, 80])  # 100, 80, 70, 50, 30, 10
        arr_instep = np.array([1, 1, 1, 2, 6, 15, 15])  # 0, 5, 6, 4, 2, 1
        self.buy_position = pd.DataFrame(data=np.vstack((arr_indicator, arr_position, arr_instep)).T,
                                         columns=["indicator", "position", "instep"])
        # 卖出分位数
        arr_indicator = np.array([75, 80, 85, 90, 95, 100])
        arr_position = np.array([90, 80, 60, 40, 20, 0])
        arr_outstep = np.array([2, 2, 4, 4, 4, 0])
        self.sell_position = pd.DataFrame(data=np.vstack((arr_indicator, arr_position, arr_outstep)).T,
                                          columns=["indicator", "remain_position", "outstep"])
        self.indicator_column_name = indicator_column_name
        self.valuation_reduce = valuation_reduce
        # 加载指数数据
        self.index_data = pd.read_csv(
            "I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\index_" + index_code + "_data.csv",
            index_col=0, header=0)
        # 获取MACD指标
        self.index_macd = dp.get_indicator_macd(index_data=self.index_data)
        # 剔除指标列有Nan的数据
        self.index_data.dropna(axis=0, how="any", inplace=True, subset=[self.indicator_column_name])
        self.index_data["date"] = pd.to_datetime(self.index_data["date"])
        self.ref_indicator = self.index_data[["date", self.indicator_column_name]]
        self.trend_sell = False  # 是否到达75百分位
        self.trend_buy = False
        self.index_code = index_code
        super().__init__(strategy_name="基础估值趋势策略")

    def operate(self, date, position):
        """
        根据指数数据判断预期仓位
        :param:    date, 要进行计算仓位的当天
        :return:   tuple, 第一个值为预期仓位百分数，第二个值为当前估值百分位
        """
        # 判断指标
        part_data = self.ref_indicator[self.ref_indicator["date"] == date][self.indicator_column_name]
        # 使用百分位做指标之前要有一定的数据量，否则没那么准确
        if len(part_data) == 0 or len(self.ref_indicator[self.ref_indicator["date"] <= date]) <= 200:
            return None, None, None
        indicator = int(round(part_data.iloc[0], 2) * 100)
        index_data = self.index_data[self.index_data["date"] == date]
        if len(index_data) > 0:
            if index_data.iloc[0]["y10_pe_ttm_fs_ewpvo_cvpos"] is np.nan and index_data.iloc[0][
                "y10_pb_fs_ew_cvpos"] is np.nan:
                return None, None, None
            elif index_data.iloc[0]["y10_pe_ttm_fs_ewpvo_cvpos"] is np.nan:
                sold_out_indicator = index_data.iloc[0]["y10_pb_fs_ew_cvpos"]
            elif index_data.iloc[0]["y10_pb_fs_ew_cvpos"] is np.nan:
                sold_out_indicator = index_data.iloc[0]["y10_pe_ttm_fs_ewpvo_cvpos"]
            else:
                sold_out_indicator = (index_data.iloc[0]["y10_pb_fs_ew_cvpos"] + index_data.iloc[0][
                    "y10_pe_ttm_fs_ewpvo_cvpos"]) / 2
        if indicator <= 30:
            self.trend_sell = False
            # 判断是否进行趋势加仓
            if self.trend_buy:  # 趋势加仓部分 and position >= 80

                # 获取两日的中长期均线并判断
                # 通过均线指标判断
                data_before_3 = self.index_data[self.index_data["date"] < date][
                    ["ma_51", "ma_20", "ma_120", "cp"]].tail(3)
                # 短期均线趋势: 1.中短期均线向上  2.收盘点在中长线上
                if (data_before_3["ma_20"].pct_change().fillna(0) >= 0).all() \
                        and (
                        (data_before_3["cp"] > data_before_3["ma_51"]).all() and (
                        data_before_3["cp"] > data_before_3["ma_20"])).all() \
                        and (data_before_3["cp"] > data_before_3["ma_120"]).all() \
                        and (data_before_3["ma_20"] > data_before_3["ma_51"]).all():
                    if (data_before_3["ma_20"] > data_before_3["ma_120"]).all():
                        return 100, indicator, "in"
                    return 90, indicator, "in"
            buy_position = self.buy_position[self.buy_position["indicator"] <= indicator]  # 买入的仓位表
            if len(buy_position) > 0:
                instep = buy_position["instep"].iloc[0]  # 每次买入的份额步长因子
                forecast_position = buy_position["position"].iloc[0]  # 预期仓位
                ref_indicator = buy_position["indicator"].iloc[0]
                forecast_position = forecast_position - (indicator - ref_indicator) * instep
                if len(buy_position) == 1:
                    self.trend_buy = True
                return forecast_position, indicator, "in"
            # or self.trend_sell
        elif indicator >= 75:
            self.trend_sell = True
            self.trend_buy = False
            indicator = sold_out_indicator
            data_before_3 = self.index_data[self.index_data["date"] < date][["ma_51", "ma_20", "cp"]].tail(
                3)  # 获取三天前的数据
            reduce_factor = 0.2 if ((data_before_3["ma_51"] - data_before_3["cp"]) > 0).all() else 0.5 if (
                    (data_before_3["ma_20"] - data_before_3["cp"]) > 0).all() else -1
            if reduce_factor > 0:
                if reduce_factor == 0.2:
                    self.trend_sell = False
                return reduce_factor * 100, indicator, "out"  # 趋势减仓
            if self.valuation_reduce:  # 估值减仓
                sell_position = self.sell_position[self.sell_position["indicator"] >= indicator]
                if len(sell_position) > 0:
                    outstep = sell_position["outstep"].iloc[0]
                    diff_indicator = sell_position["indicator"].iloc[0] - indicator  # 指标差
                    forecast_position = sell_position["remain_position"].iloc[0] + diff_indicator * outstep
                    return forecast_position, indicator, "out"
        return None, None, None