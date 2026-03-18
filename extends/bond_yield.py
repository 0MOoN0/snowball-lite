import pandas as pd
import xalpha as xa
import requests


class BondYield:

    def __init__(self):
        self.bond_yield = None

    def get_bond_yield(self):
        """
        从磁盘上获取十年期国债收益率

        """
        if self.bond_yield is None:
            self.bond_yield = pd.read_csv('I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\bond_yeild.csv',
                                          encoding='gbk',
                                          index_col=0, header=0)
        return self.bond_yield

    def update_bond_yield(self, topath=None):
        """
        更新十年期国债收益率，无法更新与目前数据的日期相差超过一年的国债收益率

        :param topath: str, 要保存的路径
        :return:
        """
        if topath is None:
            topath = 'I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\bond_yeild.csv'
        by = self.get_bond_yield()
        yesterday = xa.cons.yesterdaydash()
        if by['日期'][0] == yesterday:
            return self.bond_yield
        if xa.cons.day_diff(by['日期'][0], yesterday) < 360:
            by_diff = self._bond_china_yield(by['日期'][0], yesterday)
            if by_diff is not None and by_diff.size > 0:  # 剔除可能为非交易日的情况
                by_diff.drop(['3月', '6月', '1年', '3年', '5年', '7年', '30年'], axis=1, inplace=True)
                self.bond_yield = pd.concat([by_diff, self.bond_yield[1:]], ignore_index=True)
                self.bond_yield.to_csv('I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\bond_yeild.csv', encoding='gbk')
        return self.bond_yield

    def _bond_china_yield(start_date="2019-02-04", end_date="2020-02-04"):
        """
        中国债券信息网-国债及其他债券收益率曲线
        https://www.chinabond.com.cn/
        http://yield.chinabond.com.cn/cbweb-pbc-web/pbc/historyQuery?startDate=2019-02-07&endDate=2020-02-04&gjqx=0&qxId=ycqx&locale=cn_ZH
        注意: end_date - start_date 应该小于一年
        :param start_date: str, 需要查询的日期, 返回在该日期之后一年内的数据
            gjqx 为收益率的年限
        :param end_date: str, 需要查询的日期, 返回在该日期之前一年内的数据
        :return: pd.DateFrame, 返回在指定日期之间之前一年内的数据
        """
        url = "http://yield.chinabond.com.cn/cbweb-pbc-web/pbc/historyQuery"
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "gjqx": "10",
            "qxId": "hzsylqx",
            "locale": "cn_ZH",
        }
        headers = {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        }
        res = requests.get(url, params=params, headers=headers)
        data_text = res.text.replace("&nbsp", "")
        data_df = pd.read_html(data_text, header=0)[1]
        return data_df
