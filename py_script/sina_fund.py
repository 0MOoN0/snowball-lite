import pandas as pd
import requests

"""
根据新浪财经对债券基金进行分类，分为纯债或其他基金，根据类型分为开放式或封闭式等
"""


def sina_fund(code):
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
    if code is None:
        return
    url = "https://stock.finance.sina.com.cn/fundInfo/api/openapi.php/FundPageInfoService.tabjjgk?symbol=" + code + "&format=json&callback=jQuery1112037093315078981415_1610775746813&_=1610775746826"
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
    }
    res = requests.get(url, headers=headers)
    # data_text = res.text.replace("&nbsp", "")
    # data_df = pd.read_html(data_text, header=0)[1]
    return res.text


bond_fund = pd.read_csv('I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\bond_fund.csv', encoding='gbk', index_col=0,
                        header=0)
# for code in bond_fund.index:
for code in bond_fund.index:
    print("fetching the %s's data" % (code))
    str_source = sina_fund(code[0:6])
    df = str_source.encode("utf-8").decode("unicode_escape").replace('\\', '').replace('"', '').replace('<br/>', '')
    df_split = df.split(',')
    bf_work_type = df_split[8].split(':')[1]  # work type
    bf_type = df_split[10].split(':')[1]  # is Bond Only
    bond_fund.loc[code, 'type2'] = bf_work_type
    bond_fund.loc[code, 'type3'] = bf_type

bond_fund.to_csv('I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\bond_fund.csv', encoding='gbk')