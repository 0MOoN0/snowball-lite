import numpy as np
import pandas as pd


class Positions:
    """
    模拟持仓表，数字的单位为%
    """


class BondPositions(Positions):
    """
    债券相关仓位，包括债券基金，场内国债等
    """

    def __init__(self, max_positions=80):
        self.max_positions = max_positions
        # 十年期国债收益率
        bond_yield = np.array([3, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0])
        # 最大仓位
        max_position = np.array(self.max_positions).repeat(len(bond_yield))
        # 时点仓位
        point_position = np.array(
            [0, -1, 3.5, 5.92, 10, 16.89, 28.55, 48.25, 53.25, 64.25, 68.25, 73.25, 78.25, 83.25, 88.25,
             93.25, 98.25])  # 时点仓位，-1表示正常持有
        # 预期仓位（实际仓位）
        forecast_position = max_position * (point_position / 100)  # 使用Numpy的广播机制计算时点仓位
        forecast_position[1] = -1  # -1表示正常持有
        point_position[1] = -1
        # 数组合并，并转为DataFrame
        self.bond_positions = pd.DataFrame(
            data=np.vstack((bond_yield, max_position, point_position, forecast_position)).T,
            columns=["bond_yield", "max_position", "point_position", "forecast_position"])
        super().__init__()


class StockPositions(Positions):
    """
    股票相关仓位，股票指数基金等
    """

    def __init__(self, max_positions=100):
        # 买入分位数
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

        self.stock_position = pd.read_excel("I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\StockPositions.xls",
                                            index_col=0, header=0, dtype={"index_code": str, "fund": str})
        # A股资产分配表[资产类型：最大分配数]
        self.category_max_position = self.stock_position.groupby(
            ["category", "category_max_position"]).sum().reset_index()[["category", "category_max_position"]]
        # 市场指数分配表[市场指数类型：最大分配数]
        self.section_max_position = self.stock_position.groupby(
            ["section", "section_max_position"]).sum().reset_index()[["section", "section_max_position"]]
        super().__init__()
