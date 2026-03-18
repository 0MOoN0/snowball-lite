# python相关的脚本文件
import pandas as pd
import numpy as np
import requests


def bond_china_yield(start_date="2019-02-04", end_date="2020-02-04"):
    """
    中国债券信息网-国债及其他债券收益率曲线
    https://www.chinabond.com.cn/
    http://yield.chinabond.com.cn/cbweb-pbc-web/pbc/historyQuery?startDate=2019-02-07&endDate=2020-02-04&gjqx=0&qxId=ycqx&locale=cn_ZH
    注意: end_date - start_date 应该小于一年
    :param start_date: 需要查询的日期, 返回在该日期之后一年内的数据
        gjqx 为收益率的年限
    :type start_date: str
    :param end_date: 需要查询的日期, 返回在该日期之前一年内的数据
    :type end_date: str
    :return: 返回在指定日期之间之前一年内的数据
    :rtype: pandas.DataFrame
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


# 获取所有债券收益率信息
start_time = '2020-01-13'
end_time = '2021-01-13'
data_df = bond_china_yield(start_time, end_time)
data_df.drop(['3月', '6月', '1年', '3年', '5年', '7年', '30年'], axis=1, inplace=True)
result = data_df
while data_df is not None and data_df.size > 0:
    end_time = start_time
    start_time = start_time.replace(start_time[:4], str(int(start_time[:4]) - 1))
    data_df = bond_china_yield(start_time, end_time)
    data_df.drop(['3月', '6月', '1年', '3年', '5年', '7年', '30年'], axis=1, inplace=True)
    result = pd.concat([result, data_df], axis=0)
result.tail(10)

# 保存到csv
result.to_csv('I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\bond_yeild.csv', encoding='gbk')

# 保存到excel
result.to_excel('I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\bond_yeild.xls', sheet_name='bond_yeild',
                encoding='gbk')
